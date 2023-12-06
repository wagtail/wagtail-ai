from .models import Prompt

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
    return [prompt.as_dict() for prompt in Prompt.objects.all()]  # type: ignore
