from typing import List

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .openai import OpenAIClient


class OpenAIBackend:
    def __init__(self):
        try:
            api_key = settings.OPENAI_API_KEY
            self.client = OpenAIClient(api_key=api_key)
        except AttributeError:
            raise ImproperlyConfigured(
                "The OPENAI_API_KEY setting must be configured to use Wagtail AI"
            )

    def prompt(self, prompt: str) -> str:
        return self.client.chat(prompt)

    def get_embedding(self, input: str) -> List[float]:
        return self.client.get_embedding(input)
