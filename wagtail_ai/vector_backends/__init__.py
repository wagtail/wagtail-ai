from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, List, Type, TypeVar, Union

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from wagtail_ai.ai_backends import get_ai_backend


if TYPE_CHECKING:
    from wagtail_ai.index import Document


ConfigClass = TypeVar("ConfigClass")
IndexClass = TypeVar("IndexClass", bound="Index")


class InvalidVectorBackendError(ImproperlyConfigured):
    pass


@dataclass(frozen=True, eq=True)
class SearchResponseDocument:
    id: Union[str, int]
    metadata: dict


class Index:
    def __init__(self, index_name):
        self.index_name = index_name

    def upsert(self, *, documents: List["Document"]):
        raise NotImplementedError

    def delete(self, *, document_ids: List[str]):
        raise NotImplementedError

    def similarity_search(
        self, query_vector, *, limit: int = 5
    ) -> List[SearchResponseDocument]:
        raise NotImplementedError


class Backend(Generic[ConfigClass, IndexClass]):
    config_class: Type[ConfigClass]
    index_class: Type[IndexClass]

    def __init__(self, config):
        try:
            ai_backend_alias = config.pop("AI_BACKEND", "default")
            self.ai_backend = get_ai_backend(ai_backend_alias)
            self.config: ConfigClass = self.config_class(**config)
        except TypeError as e:
            raise ImproperlyConfigured(
                f"Missing configuration settings for the vector backend: {e}"
            ) from e

    def __init_subclass__(cls, **kwargs):
        try:
            cls.config_class
        except AttributeError as e:
            raise AttributeError(
                f"Vector backend {cls.__name__} must specify a `config_class` class attribute"
            ) from e
        return super().__init_subclass__(**kwargs)

    def get_index(self, index_name) -> IndexClass:
        raise NotImplementedError

    def create_index(self, index_name, *, vector_size: int) -> IndexClass:
        raise NotImplementedError

    def delete_index(self, index_name):
        raise NotImplementedError


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


def get_vector_backend(*, alias="default") -> Backend:
    backend_config = get_vector_backend_config()

    try:
        config = backend_config[alias]
    except KeyError as e:
        raise InvalidVectorBackendError(
            f"No vector backend with alias '{alias}': {e}"
        ) from e

    try:
        imported = import_string(config["BACKEND"])
    except ImportError as e:
        raise InvalidVectorBackendError(
            f"Couldn't import backend {config['BACKEND']}: {e}"
        ) from e

    params = config.copy()
    params.pop("BACKEND")

    return imported(params)
