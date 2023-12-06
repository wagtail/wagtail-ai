import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

DEFAULT_PROMPTS = [
    {
        "uuid": "fe029b02-833e-49d6-8002-14619962946a",  # This is a static UUID used to identify the prompt
        "label": "AI Correction",
        "description": "Correct grammar and spelling",
        "prompt": (
            "You are assisting a user in writing content for their website. "
            "The user has provided some text (following the colon). "
            "Return the provided text but with corrected grammar, spelling and punctuation. "
            "Do not add additional punctuation, quotation marks or change any words:"
        ),
        "method": "replace",
    },
    {
        "uuid": "cc4805e3-abb6-4a09-b71c-b5543af34eb1",  # This is a static UUID used to identify the prompt
        "label": "AI Completion",
        "description": "Get help writing more content based on what you've written",
        "prompt": (
            "You are assisting a user in writing content for their website. "
            "The user has provided some initial text (following the colon). "
            "Assist the user in writing the remaining content:"
        ),
        "method": "append",
    },
]


class Prompt(models.Model):
    class Method(models.TextChoices):
        REPLACE = "replace", _("Replace content")
        APPEND = "append", _("Append after existing content")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255)
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
        default=Method.REPLACE,
        help_text=_("The method used for processing the responses to the prompt."),
    )

    def __str__(self):
        return self.label

    def is_default_prompt(self) -> bool:
        """
        Returns True if the prompt is one of the default prompts.
        """
        return str(self.uuid) in [prompt["uuid"] for prompt in DEFAULT_PROMPTS]

    def get_default_prompt_value(self) -> str:
        """
        Return the default prompt value from DEFAULT_PROMPTS.
        """
        return next(
            (
                prompt["prompt"]
                for prompt in DEFAULT_PROMPTS
                if prompt["uuid"] == str(self.uuid)
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
            "uuid": str(self.uuid),
            "label": self.label,
            "description": self.description,
            "prompt": self.prompt_value,
            "method": self.Method(self.method).value,
        }
