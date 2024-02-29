import logging

from django.db.models.signals import post_save
from wagtail.images import get_image_model
from wagtail.images.models import AbstractImage

from .ai.openai import DescribeImageError, OpenAIBackend

logger = logging.getLogger(__name__)


def generate_image_title(sender, instance: "AbstractImage", **kwargs) -> None:
    # Only run on new images
    if not kwargs["created"]:
        return

    backend = OpenAIBackend()

    rendition = instance.get_rendition("max-1000x1000")

    # TODO: Add support for adding different languages here.
    prompt = (
        "Describe this image. Make the description suitable for use as an alt-text."
    )

    character_limit = get_image_model()._meta.get_field("title").max_length

    if character_limit is not None:
        prompt += f" Make the description less than {character_limit} characters long."

    try:
        description = backend.describe_image(image_file=rendition.file, prompt=prompt)
    except DescribeImageError:
        logger.exception("There was an issue describing the image.")
        return

    if not description:
        return

    description = description[:character_limit]
    instance.title = description
    instance.save(update_fields=["title"])


def register_signals():
    image_model = get_image_model()
    post_save.connect(
        generate_image_title,
        sender=image_model,
        dispatch_uid="wagtail_ai.signal_handlers.generate_image_title",
    )


register_signals()
