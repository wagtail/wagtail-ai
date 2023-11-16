from collections.abc import Mapping
from typing import Any, Required, TypedDict, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from wagtail_ai.ai.base import AIBackend


class InvalidAIBackendError(ImproperlyConfigured):
    def __init__(self, alias):
        super().__init__(f"Invalid AI backend: {alias}")


class AIBackendSettings(TypedDict):
    CLASS: Required[str]
    CONFIG: Required[Any]


def get_ai_backends_settings() -> Mapping[str, AIBackendSettings]:
    try:
        return settings.WAGTAIL_AI_BACKENDS
    except AttributeError:
        return {
            "default": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {},
            },
        }


def get_ai_backend_settings(alias: str) -> AIBackendSettings:
    backends_config = get_ai_backends_settings()
    try:
        return backends_config[alias]
    except (KeyError, ImportError) as e:
        raise InvalidAIBackendError(alias) from e


def get_ai_backend(alias: str) -> AIBackend:
    backend_dict = get_ai_backend_settings(alias)

    try:
        ai_backend_cls = cast(type[AIBackend], import_string(backend_dict["CLASS"]))
    except (KeyError, ImportError) as e:
        raise InvalidAIBackendError(alias) from e

    return ai_backend_cls(config=backend_dict["CONFIG"])
