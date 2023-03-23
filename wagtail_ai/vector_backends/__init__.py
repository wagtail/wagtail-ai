from dataclasses import dataclass
from typing import Generic, List, Type, TypeVar

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.module_loading import import_string

from wagtail_ai.ai_backends import get_ai_backend
from wagtail_ai.embedding import EmbeddingService
from wagtail_ai.index import VectorIndex, get_vector_indexes


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

    def _get_instance_embeddings(self, instance: models.Model):
        service = EmbeddingService()
        return service.embeddings_for_instance(instance)

    def _get_instance_metadata(self, instance: models.Model):
        content_type = ContentType.objects.get_for_model(instance)
        return {"content_type": content_type.pk, "object_id": instance.pk}

    def _get_indexes(self) -> List[Type[VectorIndex]]:
        return get_vector_indexes()

    def search(self, query, queryset):
        raise NotImplementedError

    def rebuild_indexes(self):
        raise NotImplementedError


def get_vector_backend_config():
    try:
        vector_backends = settings.WAGTAIL_AI_VECTOR_BACKENDS
    except AttributeError:
        vector_backends = {
            "default": {
                "BACKEND": "wagtail_ai.vector_backends.qdrant.QdrantBackend",
                "API_KEY": "",
                "HOST": "",
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

    config.pop("BACKEND")

    return imported(config)
