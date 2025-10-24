from typing import cast
from urllib.parse import SplitResult

import pytest
from django.core.exceptions import ValidationError
from pytest_django import DjangoAssertNumQueries
from wagtail.images.models import Image
from wagtail_factories import ImageFactory

from wagtail_ai.context import PromptContext


def test_missing_key() -> None:
    context = PromptContext(name="Gordon", role="Scientist")
    prompt = "My name is {name} and I am a {role}. I work at {company}."
    context.clean(prompt)
    # company has no validator and is missing, so left as-is
    assert context["company"] == "{company}"
    result = prompt.format_map(context)
    assert result == "My name is Gordon and I am a Scientist. I work at {company}."


@pytest.mark.django_db
def test_image_validator(django_assert_num_queries: DjangoAssertNumQueries) -> None:
    image = cast(Image, ImageFactory())
    context = PromptContext(image=image.pk)
    prompt = "Prompt does not use the image placeholder."
    # This will not hit the database as the prompt does not use {image}
    with django_assert_num_queries(0):
        context.clean(prompt)
        assert context["image"] == image.pk
    prompt = "Describe the image with ID {image}."
    expected = image.get_rendition("max-800x600").file
    # This will fetch the image and generate a rendition
    with django_assert_num_queries(7):
        context.clean(prompt)
    # Accessing the result again should not hit the database
    with django_assert_num_queries(0):
        assert context["image"] == expected


@pytest.mark.django_db
def test_image_validator_data_url(
    image_data_url,
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    context = PromptContext(image=image_data_url)
    with django_assert_num_queries(0):
        context.clean("Describe the following image: {image}")
        assert isinstance(context["image"], SplitResult)
        assert context["image"].geturl() == image_data_url


@pytest.mark.django_db
def test_image_validator_invalid_data_url(
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    data_url = "data:text/plain;base64,SGVsbG8sIFdvcmxkIQ=="
    context = PromptContext(image=data_url)
    with django_assert_num_queries(0), pytest.raises(ValidationError) as exc_info:
        context.clean("Describe the following image: {image}")
    assert str(exc_info.value.message) == "The provided data URL is not an image."


def test_image_validator_missing() -> None:
    context = PromptContext()
    with pytest.raises(ValidationError) as exc_info:
        context.clean("Describe the image with ID {image}.")
    assert (
        str(exc_info.value.message)
        == "The prompt requires an image, but none was provided."
    )


@pytest.mark.django_db
def test_image_validator_not_found() -> None:
    context = PromptContext(image=9999999)
    with pytest.raises(ValidationError) as exc_info:
        context.clean("Describe the image with ID {image}.")
    assert str(exc_info.value.message) == "Could not find image with id 9999999."
