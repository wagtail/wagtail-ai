import json
from typing import cast

import pytest
from django.core.exceptions import ValidationError
from pytest_django import DjangoAssertNumQueries
from wagtail.images.models import Image
from wagtail_factories import ImageFactory

from wagtail_ai.context import PromptContext, PromptJSONDecoder


def test_missing_key():
    context = PromptContext(name="Gordon", role="Scientist")
    prompt = "My name is {name} and I am a {role}. I work at {company}."
    context.clean(prompt)
    # company has no validator and is missing, so left as-is
    assert context["company"] == "{company}"
    result = prompt.format_map(context)
    assert result == "My name is Gordon and I am a Scientist. I work at {company}."


def test_json_decoder():
    json_str = '{"name": "Gordon", "role": "Scientist"}'
    context = json.loads(json_str, cls=PromptJSONDecoder)
    assert isinstance(context, PromptContext)
    prompt = "Write an introduction for {name}, a {role}."
    context.clean(prompt)
    result = prompt.format_map(context)
    assert result == "Write an introduction for Gordon, a Scientist."


@pytest.mark.django_db
def test_image_id_validator(django_assert_num_queries: DjangoAssertNumQueries):
    image = cast(Image, ImageFactory())
    context = PromptContext(image_id=image.pk)
    prompt = "Prompt does not use the image_id placeholder."
    # This will not hit the database as the prompt does not use {image_id}
    with django_assert_num_queries(0):
        context.clean(prompt)
        assert context["image_id"] == image.pk
    prompt = "Describe the image with ID {image_id}."
    expected = image.get_rendition("max-800x600").file
    # This will fetch the image and generate a rendition
    with django_assert_num_queries(7):
        context.clean(prompt)
    # Accessing the result again should not hit the database
    with django_assert_num_queries(0):
        assert context["image_id"] == expected


def test_image_id_validator_missing():
    context = PromptContext()
    with pytest.raises(ValidationError) as exc_info:
        context.clean("Describe the image with ID {image_id}.")
    assert (
        str(exc_info.value.message)
        == "The prompt requires an image, but none was provided."
    )


@pytest.mark.django_db
def test_image_id_validator_not_found():
    context = PromptContext(image_id=9999999)
    with pytest.raises(ValidationError) as exc_info:
        context.clean("Describe the image with ID {image_id}.")
    assert str(exc_info.value.message) == "Could not find image with id 9999999."
