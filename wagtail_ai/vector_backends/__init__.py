from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, List, Type, TypeVar

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.module_loading import import_string

from wagtail_ai.ai_backends import get_ai_backend


if TYPE_CHECKING:
    from wagtail_ai.index import VectorIndex


ConfigClass = TypeVar("ConfigClass")


class InvalidVectorBackendError(ImproperlyConfigured):
    pass


@dataclass
class QueryResponse:
    content: str
    sources: List[models.Model]


class Backend(Generic[ConfigClass]):
    config_class: Type[ConfigClass]

    def __init__(self, config):
        try:
            ai_backend_alias = config.pop("AI_BACKEND", "default")
            self.ai_backend = get_ai_backend(ai_backend_alias)
            self.config: ConfigClass = self.config_class(**config)
        except TypeError as e:
            raise ImproperlyConfigured(
                f"Missing configuration settings for the vector backend: {e}"
            )

    def __init_subclass__(cls, **kwargs):
        try:
            cls.config_class
        except AttributeError:
            raise AttributeError(
                f"Vector backend {cls.__name__} must specify a `config_class` class attribute"
            )
        return super().__init_subclass__(**kwargs)

    def _get_indexes(self) -> List["VectorIndex"]:
        from wagtail_ai.index import get_vector_indexes

        return get_vector_indexes()

    def search(self, index_class, query_embedding, *, limit: int = 5) -> List[dict]:
        raise NotImplementedError

    def _build_index(self, index: "VectorIndex"):
        raise NotImplementedError

    def rebuild_indexes(self):
        for index in self._get_indexes():
            try:
                index._pre_build_index()
            except AttributeError:
                # It's not a problem if the index doesn't specify a `pre_build_index` hook
                pass
            self._build_index(index)


def get_vector_backend_config():
    try:
        vector_backends = settings.WAGTAIL_AI_VECTOR_BACKENDS
    except AttributeError:
        vector_backends = {
            "default": {
                "BACKEND": "wagtail_ai.vector_backends.numpy.NumpyBackend",
            }
        }

    return vector_backends


def get_vector_backend(alias="default") -> Backend:
    backend_config = get_vector_backend_config()

    try:
        config = backend_config[alias]
    except KeyError as e:
        raise InvalidVectorBackendError(f"No vector backend with alias '{alias}': {e}")

    try:
        imported = import_string(config["BACKEND"])
    except ImportError as e:
        raise InvalidVectorBackendError(
            f"Couldn't import backend {config['BACKEND']}: {e}"
        )

    params = config.copy()
    params.pop("BACKEND")

    return imported(params)
