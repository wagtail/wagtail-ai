import every_ai
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from every_ai import AIBackend


class InvalidAIBackendError(ImproperlyConfigured):
    def __init__(self, alias):
        super().__init__(f"Invalid AI backend: {alias}")


def get_ai_backend_config():
    try:
        ai_backends = settings.WAGTAIL_AI_BACKENDS
    except AttributeError:
        ai_backends = {
            "default": {
                "BACKEND": "openai",
            }
        }

    return ai_backends


def get_ai_backend(alias="default") -> AIBackend:
    backend_config = get_ai_backend_config()

    try:
        config = backend_config[alias]
        config_settings = config.get("CONFIG", {})
        backend = every_ai.init(config["BACKEND"], **config_settings)
    except (KeyError, ImportError) as e:
        raise InvalidAIBackendError(alias) from e

    return backend
