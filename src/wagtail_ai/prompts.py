from collections.abc import Sequence
from typing import NotRequired, Required, TypedDict


class PromptDict(TypedDict):
    default_prompt_id: Required[int]
    label: Required[str]
    description: NotRequired[str]
    prompt: Required[str]
    method: Required[str]


DEFAULT_PROMPTS: Sequence[PromptDict] = [
    {
        "default_prompt_id": 1,  # A unique ID used to identify and manage default prompts
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
        "default_prompt_id": 2,  # A unique ID used to identify and manage default prompts
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
