import uuid

DEFAULT_PROMPTS = [
    {
        "uuid": uuid.UUID("fe029b02-833e-49d6-8002-14619962946a"),
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
        "uuid": uuid.UUID("cc4805e3-abb6-4a09-b71c-b5543af34eb1"),
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
