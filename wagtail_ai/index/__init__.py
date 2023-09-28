from .base import VectorIndex
from .model import (
    get_indexed_models,
)
from .registry import registry


def get_vector_indexes() -> dict[str, VectorIndex]:
    models = get_indexed_models()
    for model in models:
        registry.register()(model.get_vector_index().__class__)

    # TODO fix this - do we need to pass object_type to the instantiated index?
    final = {}
    for model in models:
        cls = model.get_vector_index().__class__
        final[cls.__name__] = cls(object_type=model.__class__)

    return final
