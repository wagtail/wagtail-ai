from django.db import models

from .prompts import Prompt as PromptDataClass


class Prompt(models.Model):
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
        choices=PromptDataClass.Method.choices,
        default=PromptDataClass.Method.REPLACE,
        help_text="The method used for processing a prompt's response.",
    )

    def __str__(self):
        return self.label
