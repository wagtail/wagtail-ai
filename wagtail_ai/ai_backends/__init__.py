import os

from typing import List, Optional, Protocol, Type, TypeVar

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


class InvalidAIBackendError(ImproperlyConfigured):
    pass


ConfigClass = TypeVar("ConfigClass")


class Backend(Protocol[ConfigClass]):
    config_class: Type[ConfigClass]

    def prompt(
        self, *, system_messages: Optional[List[str]] = None, user_messages: List[str]
    ) -> str:
        ...

    def get_embeddings(self, inputs: List[str]) -> List[List[float]]:
        ...

    @property
    def embedding_dimensions(self) -> int:
        ...


def get_ai_backend_config():
    try:
        ai_backends = settings.WAGTAIL_AI_BACKENDS
    except AttributeError:
        ai_backends = {
            "default": {
                "BACKEND": "wagtail_ai.ai_backends.openai.OpenAIBackend",
                "API_KEY": os.environ.get("OPENAI_API_KEY"),
            }
        }

    return ai_backends


def get_ai_backend(alias="default") -> Backend:
    backend_config = get_ai_backend_config()

    try:
        config = backend_config[alias]
    except KeyError as e:
        raise InvalidAIBackendError(f"No AI backend with alias '{alias}': {e}")

    try:
        imported = import_string(config["BACKEND"])
    except ImportError as e:
        raise InvalidAIBackendError(f"Couldn't import backend {config['BACKEND']}: {e}")

    params = config.copy()
    params.pop("BACKEND")

    return imported(params)
