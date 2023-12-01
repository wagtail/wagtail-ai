import inspect
from dataclasses import dataclass
from typing import Union

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import gettext_lazy as _


@dataclass(kw_only=True)
class Prompt:
    class Method(models.TextChoices):
        REPLACE = "replace", _("Replace content")
        APPEND = "append", _("Append after existing content")

    class DoesNotExist(Exception):
        pass

    id: int
    label: str
    prompt: str
    backend: str = "default"
    description: str = ""
    method: Union[str, Method] = Method.REPLACE

    def __post_init__(self):
        self.prompt = inspect.cleandoc(self.prompt)
        self.method = Prompt.Method(self.method)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "prompt": self.prompt,
            "method": Prompt.Method(self.method).value,
        }


DEFAULT_PROMPTS = [
    {
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


def get_prompts() -> list[Prompt]:
    from .models import Prompt as PromptModel  # Avoid circular import

    try:
        return [
            Prompt(
                label=prompt.label,
                description=prompt.description,
                prompt=prompt.prompt,
                method=prompt.method,
                id=idx,
            )
            for idx, prompt in enumerate(PromptModel.objects.all())  # type: ignore
        ]
    except TypeError as e:
        raise ImproperlyConfigured(
            """WAGTAIL_AI_PROMPTS must be a list of dictionaries, where each dictionary
            has a 'label', 'description', 'prompt' and 'method' key.
            The 'method' must be one of 'append' or 'replace'."""
        ) from e


def get_prompt_by_id(id: int) -> Prompt:
    for prompt in get_prompts():
        if prompt.id == id:
            return prompt
    raise Prompt.DoesNotExist(f"Can't get prompt by id: {id}")
