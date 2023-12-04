from django.db import models
from django.utils.translation import gettext_lazy as _


class Prompt(models.Model):
    class Method(models.TextChoices):
        REPLACE = "replace", _("Replace content")
        APPEND = "append", _("Append after existing content")

    label = models.CharField(max_length=255)
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="A description of the prompt to be displayed alongside it's label.",
    )
    prompt = models.TextField(
        help_text=("The text prompt sent to the AI (e.g. ChatGPT) to generate content.")
    )
    method = models.CharField(
        max_length=25,
        choices=Method.choices,
        default=Method.REPLACE,
        help_text="The method used for processing a prompt's response.",
    )

    def __str__(self):
        return self.label

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "prompt": self.prompt,
            "method": self.Method(self.method).value,
        }
