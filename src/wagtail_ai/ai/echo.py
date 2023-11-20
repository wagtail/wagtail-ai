import random
import time
from collections.abc import Generator, Iterator
from typing import Any, NotRequired, TypedDict

from .base import AIBackend, AIResponse, ChatModelConfig


class EchoResponse(AIResponse):
    _text: str | None = None
    response_iterator: Iterator[str]

    def __init__(self, response_iterator: Iterator[str]) -> None:
        self.response_iterator = response_iterator

    def __iter__(self) -> Iterator[str]:
        return self.response_iterator

    def text(self) -> str:
        if self._text is not None:
            return self._text
        self._text = " ".join(self.response_iterator)
        return self._text


class EchoBackendConfig(TypedDict):
    MAX_WORD_SLEEP_SECONDS: NotRequired[int]


class EchoBackend(AIBackend[EchoBackendConfig, ChatModelConfig]):
    max_word_sleep_seconds: int = 1

    def init_config(
        self,
        *,
        backend_config: EchoBackendConfig | None,
        chat_model_config: ChatModelConfig,
    ) -> None:
        if backend_config is not None:
            try:
                self.max_word_sleep_seconds = int(
                    backend_config["MAX_WORD_SLEEP_SECONDS"]
                )
            except KeyError:
                pass

    def prompt(self, *, prompt: str, content: str, **kwargs: Any) -> EchoResponse:
        def response_iterator() -> Generator[str, None, None]:
            response = ["This", "is", "an", "echo", "backend:"]
            response += content.split()
            for word in response:
                if (
                    self.max_word_sleep_seconds is not None
                    and self.max_word_sleep_seconds > 0
                ):
                    time.sleep(
                        random.random() * random.randint(0, self.max_word_sleep_seconds)
                    )
                yield word

        return EchoResponse(response_iterator())
