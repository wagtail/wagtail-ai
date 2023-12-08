import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.search import index

from wagtail_ai.prompts import DEFAULT_PROMPTS


class Prompt(models.Model, index.Indexed):
    class Method(models.TextChoices):
        REPLACE = "replace", _("Replace content")
        APPEND = "append", _("Append after existing content")

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    default_prompt_id = models.SmallIntegerField(unique=True, editable=False, null=True)
    label = models.CharField(max_length=50)
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "The prompt description, displayed alongside its label on the settings listing."
        ),
    )
    prompt = models.TextField(  # noqa: DJ001
        null=True,
        blank=False,
        help_text=_(
            "The prompt text sent to the Large Language Model (e.g. ChatGPT) to generate content."
        ),
    )
    method = models.CharField(
        max_length=25,
        choices=Method.choices,
        help_text=_("The method used for processing the responses to the prompt."),
    )

    search_fields = [
        index.AutocompleteField("label"),
        index.SearchField("description"),
        index.SearchField("prompt"),
    ]

    def __str__(self):
        return self.label

    def is_default_prompt(self) -> bool:
        """
        Returns True if the prompt is one of the default prompts.
        """
        return self.default_prompt_id is not None

    def get_default_prompt_value(self) -> str:
        """
        Return the default prompt value from DEFAULT_PROMPTS.
        """
        return next(
            (
                prompt["prompt"]
                for prompt in DEFAULT_PROMPTS
                if prompt["default_prompt_id"] == self.default_prompt_id
            ),
            None,
        )

    @property
    def prompt_value(self) -> str | None:
        """
        Return the prompt value, otherwise if the prompt is None and belongs
        to the default prompts, map to the default prompt value.
        """
        if self.prompt is None and self.is_default_prompt():
            return self.get_default_prompt_value()
        return self.prompt

    def as_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "label": self.label,
            "description": self.description,
            "prompt": self.prompt_value,
            "method": self.Method(self.method).value,
        }
