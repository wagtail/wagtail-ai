from abc import ABCMeta, abstractmethod
from collections.abc import Iterator
from typing import Generic, Protocol, TypeVar


class AIResponse(Protocol):
    """
    Compatible with the llm.Response.
    """

    def __iter__(self) -> Iterator[str]:
        ...

    def text(self) -> str:
        ...


AIBackendConfig = TypeVar("AIBackendConfig")


class AIBackend(Generic[AIBackendConfig], metaclass=ABCMeta):
    config: AIBackendConfig

    def __init__(self, *, config: AIBackendConfig) -> None:
        self.init_config(config)

    def init_config(self, config: AIBackendConfig) -> None:
        """
        Take the settings dictionary and parse it onto the backend's instance.

        This method is meant to be overriden by subclasses and is optional.
        """
        pass

    @abstractmethod
    def prompt(self, prompt: str, content: str) -> AIResponse:
        """
        Given a prompt and a content, return a response.
        """
        ...
