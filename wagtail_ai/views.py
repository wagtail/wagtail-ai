import inspect
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse

from .openai import OpenAIClient


COMPLETION_PROMPT = inspect.cleandoc(
    """You are assisting a user in writing content for their website.
    The user has provided some initial text (following the colon).
    Assist the user in writing the remaining content:"""
)

CORRECTION_PROMPT = inspect.cleandoc(
    """You are assisting a user in writing content for their website.
    The user has provided some text (following the colon).
    Return the provided text but with corrected grammar, spelling and punctuation.
    Do not add additional punctuation, quotation marks or change any words:"""
)


def build_openai_client() -> OpenAIClient:
    try:
        api_key = settings.OPENAI_API_KEY
        return OpenAIClient(api_key=api_key)
    except AttributeError:
        raise ImproperlyConfigured(
            "The OPENAI_API_KEY setting must be configured to use Wagtail AI"
        )


def ai_process(request):
    text = request.GET.get("text")
    action = request.GET.get("action", "completion")
    prompt = COMPLETION_PROMPT if action == "completion" else CORRECTION_PROMPT
    full_prompt = "\n".join([prompt, text])
    client = build_openai_client()
    message = client.chat(full_prompt)
    # Remove extra blank lines returned by the API
    message = os.linesep.join([s for s in message.splitlines() if s])
    return JsonResponse({"message": message})
