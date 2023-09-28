from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from .base import VectorIndex


class VectorIndexRegistry:
    """A registry to keep track of all the VectorIndex classes that have been registered."""

    def __init__(self):
        self._registry: dict[str, Type["VectorIndex"]] = {}

    def register(self):
        def decorator(cls: Type["VectorIndex"]):
            self._registry[cls.__name__] = cls
            return cls

        return decorator

    def __iter__(self):
        return iter(self._registry.items())


registry = VectorIndexRegistry()
