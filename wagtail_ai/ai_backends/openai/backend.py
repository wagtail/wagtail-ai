from typing import List

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .openai import OpenAIClient


# Fixed for now until we support other models
EMBEDDING_DIMENSIONS = 1536


class OpenAIBackend:
    def __init__(self):
        try:
            api_key = settings.OPENAI_API_KEY
            self.client = OpenAIClient(api_key=api_key)
        except AttributeError:
            raise ImproperlyConfigured(
                "The OPENAI_API_KEY setting must be configured to use Wagtail AI"
            )

    def prompt(self, *, system_messages: List[str], user_messages: List[str]) -> str:
        return self.client.chat(
            system_messages=system_messages, user_messages=user_messages
        )

    def get_embedding(self, input: str) -> List[float]:
        return self.client.get_embedding(input)

    @property
    def embedding_dimensions(self) -> int:
        return EMBEDDING_DIMENSIONS
