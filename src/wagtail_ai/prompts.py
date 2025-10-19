

from collections.abc import Sequence
from typing import NotRequired, Required, TypedDict


class AgentPromptDefaults:
    @classmethod
    def page_title_prompt(cls):
        return (
            "Create an SEO-friendly page title, and respond ONLY with the title "
            "in plain text (without quotes), for the following "
            "web page content:\n\n"
            "{content_html}"
        )

    @classmethod
    def page_description_prompt(cls):
        return (
            "Create an SEO-friendly meta description, and respond ONLY with the "
            "description in plain text (without quotes) for the following web page "
            "content:\n\n"
            "{content_html}"
        )

    @classmethod
    def image_title_prompt(cls):
        return (
            "Generate a title (in plain text, no longer than "
            "{max_length} characters, without quotes) for the following image: {image}"
        )

    @classmethod
    def image_description_prompt(cls):
        return (
            "Generate a description (in plain text, no longer than "
            "{max_length} characters) for the following image: {image}"
        )

    @classmethod
    def contextual_alt_text_prompt(cls):
        return '''Generate an alt text (and only the text) for the following image:
{image}

Make the alt text relevant to the following content shown before the image:

---
{form_context_before}
---

and also relevant to the following content shown after the image:

---
{form_context_after}
---'''


class PromptDict(TypedDict):
    default_prompt_id: Required[int]
    label: Required[str]
    description: NotRequired[str]
    prompt: Required[str]
    method: Required[str]


DEFAULT_PROMPTS: Sequence[PromptDict] = [
    {
        "default_prompt_id": 1,
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
        "default_prompt_id": 2,
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
        "default_prompt_id": 5,
        "label": "Default Image Title Generator",
        "description": "Default prompt for generating image titles",
        "prompt": AgentPromptDefaults.image_title_prompt(),
        "method": "replace",
        "feature": "image_title",
    },
]
