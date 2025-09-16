import json
from string import Formatter
from typing import Any, Type, cast
from urllib.parse import SplitResult, urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils.translation import gettext as _
from wagtail.images.models import AbstractImage


class PromptContext(dict[str, Any]):
    """
    A dict-like object to interpolate a prompt string's placeholders with values.
    Provides a ``clean()`` method to validate that all placeholders can be handled.

    Validators can be registered with ``register_validator()`` to validate and
    transform a key's value or provide a fallback.

    A missing key without a registered validator is set as ``{key}`` so
    ``str.format_map()`` leaves it as-is.
    """

    validators: dict[str, Any] = {}

    @classmethod
    def register_validator(cls, name: str, validator):
        """
        Register a validator function for a given placeholder key.

        Validator functions should accept a single argument, the context
        instance, and return the value to use for the key. They can raise
        ``ValidationError`` if the key is required but invalid or missing from
        the context.
        """
        cls.validators[name] = validator

    def clean(self, prompt: str):
        """
        Validate that all placeholder keys in the prompt can be handled.
        """
        formatter = Formatter()
        placeholders = [name for _, name, *_ in formatter.parse(prompt) if name]
        for key in placeholders:
            if key in self.validators:
                # Provide the whole context to the validator to allow it to
                # access other keys if needed
                self[key] = self.validators[key](self)
            elif key not in self:
                self[key] = "{%s}" % key


class PromptJSONDecoder(json.JSONDecoder):
    """
    A JSON decoder that uses ``PromptContext`` in place of a plain ``dict``
    when parsing a JSON object.
    """

    def __init__(self, *args, object_pairs_hook=PromptContext, **kwargs):
        super().__init__(*args, object_pairs_hook=object_pairs_hook, **kwargs)


def image_id_validator(context) -> File | SplitResult | None:
    """Fetch a Wagtail image by ID and return its rendition file."""
    if "image_id" not in context:
        raise ValidationError(_("The prompt requires an image, but none was provided."))
    image_id = context["image_id"]

    # Check if it's a data URL
    try:
        url: SplitResult = urlsplit(image_id)
    except (AttributeError, ValueError):
        pass
    else:
        if url.scheme == "data":
            if url.path and url.path.startswith("image/"):
                # Return the SplitResult instead of opening the URL,
                # as some backends (e.g. OpenAI) can handle data URLs directly.
                return url
            raise ValidationError(
                _("The provided data URL is not an image."),
                code="invalid",
            )

    from wagtail.images import get_image_model

    Image = cast(Type[AbstractImage], get_image_model())
    try:
        image = Image._default_manager.get(id=image_id)
    except Image.DoesNotExist as error:
        raise ValidationError(
            _("Could not find image with id %(image_id)s.") % {"image_id": image_id}
        ) from error
    wagtail_ai_settings = getattr(settings, "WAGTAIL_AI", {})
    rendition_filter = wagtail_ai_settings.get(
        "IMAGE_DESCRIPTION_RENDITION_FILTER", "max-800x600"
    )
    rendition = image.get_rendition(rendition_filter)
    image_file = rendition.file
    return image_file


PromptContext.register_validator("image_id", image_id_validator)
