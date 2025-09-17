from collections.abc import Sequence
from enum import IntEnum
from typing import NotRequired, Required, TypedDict


class DefaultPrompt(IntEnum):
    """A unique ID used to identify and manage default prompts."""

    CORRECTION = 1
    COMPLETION = 2
    DESCRIPTION = 3
    TITLE = 4
    CONTEXTUAL_ALT_TEXT = 5
    IMAGE_TITLE = 6
    IMAGE_DESCRIPTION = 7


class PromptDict(TypedDict):
    default_prompt_id: Required[int]
    label: Required[str]
    description: NotRequired[str]
    prompt: Required[str]
    method: Required[str]


DEFAULT_PROMPTS: Sequence[PromptDict] = [
    {
        "default_prompt_id": DefaultPrompt.CORRECTION,
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
        "default_prompt_id": DefaultPrompt.COMPLETION,
        "label": "AI Completion",
        "description": "Get help writing more content based on what you've written",
        "prompt": (
            "You are assisting a user in writing content for their website. "
            "The user has provided some initial text (following the colon). "
            "Assist the user in writing the remaining content:"
        ),
        "method": "append",
    },
    {
        "default_prompt_id": DefaultPrompt.DESCRIPTION,
        "label": "AI Description",
        "description": "Generate a description by summarizing the page content",
        "prompt": (
            "Create an SEO-friendly meta description of the following web page content:\n\n"
            "{content_text}"
        ),
        "method": "replace",
    },
    {
        "default_prompt_id": DefaultPrompt.TITLE,
        "label": "AI Title",
        "description": "Generate a title based on the page content",
        "prompt": (
            "Create an SEO-friendly page title for the following web page content:\n\n"
            "{content_text}"
        ),
        "method": "replace",
    },
    {
        "default_prompt_id": DefaultPrompt.CONTEXTUAL_ALT_TEXT,
        "label": "Contextual alt text",
        "description": "Generate an alt text for the image with the relevant context",
        "prompt": """Generate an alt text (and only the text) for the following image: {image_id}

Make the alt text relevant to the following content shown before the image:

---
{form_context_before}
---

and also relevant to the following content shown after the image:

---
{form_context_after}
---
""",
        "method": "replace",
    },
    {
        "default_prompt_id": DefaultPrompt.IMAGE_TITLE,
        "label": "Image title",
        "description": "Generate a title for the image",
        "prompt": (
            "Generate a title (and only the title, no longer than "
            "{max_length} characters) for the following image: {image_id}"
        ),
        "method": "replace",
    },
    {
        "default_prompt_id": DefaultPrompt.IMAGE_DESCRIPTION,
        "label": "Image description",
        "description": "Generate a description for the image",
        "prompt": (
            "Generate a description (and only the description, no longer than "
            "{max_length} characters) for the following image: {image_id}"
        ),
        "method": "replace",
    },
]
