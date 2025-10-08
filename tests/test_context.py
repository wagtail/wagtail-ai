from typing import cast
from urllib.parse import SplitResult

import pytest
from django.core.exceptions import ValidationError
from pytest_django import DjangoAssertNumQueries
from wagtail.images.models import Image
from wagtail_factories import ImageFactory

from wagtail_ai.context import PromptContext


def test_missing_key():
    context = PromptContext(name="Gordon", role="Scientist")
    prompt = "My name is {name} and I am a {role}. I work at {company}."
    context.clean(prompt)
    # company has no validator and is missing, so left as-is
    assert context["company"] == "{company}"
    result = prompt.format_map(context)
    assert result == "My name is Gordon and I am a Scientist. I work at {company}."


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


@pytest.mark.django_db
def test_image_id_validator_data_url(
    image_data_url,
    django_assert_num_queries: DjangoAssertNumQueries,
):
    context = PromptContext(image_id=image_data_url)
    with django_assert_num_queries(0):
        context.clean("Describe the following image: {image_id}")
        assert isinstance(context["image_id"], SplitResult)
        assert context["image_id"].geturl() == image_data_url


@pytest.mark.django_db
def test_image_id_validator_invalid_data_url(
    django_assert_num_queries: DjangoAssertNumQueries,
):
    data_url = "data:text/plain;base64,SGVsbG8sIFdvcmxkIQ=="
    context = PromptContext(image_id=data_url)
    with django_assert_num_queries(0), pytest.raises(ValidationError) as exc_info:
        context.clean("Describe the following image: {image_id}")
    assert str(exc_info.value.message) == "The provided data URL is not an image."


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
