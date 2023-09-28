from dataclasses import dataclass
from typing import List, Optional

from django.core.exceptions import ImproperlyConfigured

from .openai import OpenAIClient

# Fixed for now until we support other models
EMBEDDING_DIMENSIONS = 1536


@dataclass
class BackendConfig:
    API_KEY: str = ""


class OpenAIBackend:
    config_class = BackendConfig

    def __init__(self, config: dict):
        try:
            self.config = self.config_class(**config)
            api_key = self.config.API_KEY
            self.client = OpenAIClient(api_key=api_key)
        except AttributeError as e:
            raise ImproperlyConfigured(
                "The API_KEY setting must be configured to use OpenAI"
            ) from e

    def prompt(
        self, *, system_messages: Optional[List[str]] = None, user_messages: List[str]
    ) -> str:
        return self.client.chat(
            system_messages=system_messages, user_messages=user_messages
        )

    def get_embeddings(self, inputs: List[str]) -> List[List[float]]:
        return self.client.get_embeddings(inputs)

    @property
    def embedding_dimensions(self) -> int:
        return EMBEDDING_DIMENSIONS
