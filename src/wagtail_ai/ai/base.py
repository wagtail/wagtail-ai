from abc import ABCMeta, abstractmethod
from collections.abc import Mapping
from typing import Any, Generic, TypedDict, TypeVar

from ..text_splitters.base import BaseTextSplitterLength
from ..types import AIResponse, TextSplitterProtocol


class ChatModelConfig(TypedDict):
    id: str
    token_limit: int
    extra: Mapping[str, Any] | None
    text_splitter_class: type[TextSplitterProtocol]
    text_splitter_length_class: type[BaseTextSplitterLength]


AIBackendConfig = TypeVar("AIBackendConfig")
CMC = TypeVar("CMC", bound=ChatModelConfig)


class AIBackend(Generic[AIBackendConfig, CMC], metaclass=ABCMeta):
    text_splitter_class: type[TextSplitterProtocol]
    chat_model_config: CMC

    def __init__(
        self, *, config: AIBackendConfig | None, chat_model_config: CMC
    ) -> None:
        self.chat_model_config = chat_model_config
        self.init_config(backend_config=config, chat_model_config=chat_model_config)

    def init_config(
        self, *, backend_config: AIBackendConfig | None, chat_model_config: CMC
    ) -> None:
        """
        Take the settings dictionary and parse it onto the backend's instance.

        This method is meant to be overridden by subclasses and is optional.
        """
        pass

    @abstractmethod
    def prompt(self, prompt: str, content: str) -> AIResponse:
        """
        Given a prompt and a content, return a response.
        """
        ...

    def get_text_splitter(self) -> TextSplitterProtocol:
        return self.chat_model_config["text_splitter_class"](
            chunk_size=self.chat_model_config["token_limit"],
            length_function=self.get_splitter_length,
        )

    def get_splitter_length(self, text: str) -> int:
        return self.chat_model_config[
            "text_splitter_length_class"
        ]().get_splitter_length(text)
