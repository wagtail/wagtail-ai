from typing import List, Protocol

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


class Backend(Protocol):
    def prompt(self, prompt: str) -> str:
        ...

    def get_embedding(self, input: str) -> List[float]:
        ...


def get_backend(alias="default") -> Backend:
    try:
        specified_backend = settings.WAGTAIL_AI_BACKENDS[alias]["BACKEND"]
    except AttributeError:
        specified_backend = "wagtail_ai.backends.openai.OpenAIBackend"
    except KeyError:
        raise ImproperlyConfigured(
            "The WAGTAIL_AI_BACKENDS setting must be a dictionary of alias-config pairs."
        )

    imported = import_string(specified_backend)

    return imported()
