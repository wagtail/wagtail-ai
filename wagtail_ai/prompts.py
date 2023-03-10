import inspect

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@dataclass
class Prompt:
    class Method(Enum):
        REPLACE = "replace"
        APPEND = "append"

    id: int
    label: str
    prompt: str
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
            "method": self.method.value,
        }


DEFAULT_PROMPTS = [
    {
        "label": "AI Correction",
        "description": "Correct grammar and spelling",
        "prompt": """You are assisting a user in writing content for their website.
            The user has provided some text (following the colon).
            Return the provided text but with corrected grammar, spelling and punctuation.
            Do not add additional punctuation, quotation marks or change any words:""",
        "method": "replace",
    },
    {
        "label": "AI Completion",
        "description": "Get help writing more content based on what you've written",
        "prompt": """You are assisting a user in writing content for their website.
            The user has provided some initial text (following the colon).
            Assist the user in writing the remaining content:""",
        "method": "append",
    },
]


def get_prompts():
    try:
        return [
            Prompt(**prompt, id=idx)
            for idx, prompt in enumerate(
                getattr(settings, "WAGTAIL_AI_PROMPTS", []) or DEFAULT_PROMPTS
            )
        ]
    except TypeError:
        raise ImproperlyConfigured(
            """WAGTAIL_AI_PROMPTS must be a list of dictionaries, where each dictionary
            has a 'label', 'description', 'prompt' and 'method' key.
            The 'method' must be one of 'append' or 'replace'."""
        )


def get_prompt_by_id(id: int) -> Optional[Prompt]:
    for prompt in get_prompts():
        if prompt.id == id:
            return prompt
    return None
