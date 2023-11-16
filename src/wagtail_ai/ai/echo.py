import random
import time
from collections.abc import Generator, Iterator
from typing import Any, NotRequired, TypedDict

from .base import AIBackend, AIResponse


class EchoResponse(AIResponse):
    def __init__(self, response_iterator: Iterator[str]) -> None:
        self.response_iterator = response_iterator

    def __iter__(self) -> Iterator[str]:
        return self.response_iterator

    def text(self) -> str:
        return " ".join(self.response_iterator)


class EchoBackendConfig(TypedDict):
    MIN_WORD_SLEEP_SECONDS: NotRequired[int]
    MAX_WORD_SLEEP_SECONDS: NotRequired[int]


class EchoBackend(AIBackend[EchoBackendConfig]):
    min_word_sleep_seconds: int
    max_word_sleep_seconds: int

    def init_config(self, config: EchoBackendConfig) -> None:
        self.min_word_sleep_seconds = int(config.get("MIN_WORD_SLEEP_SECONDS", 0))
        self.max_word_sleep_seconds = int(config.get("MAX_WORD_SLEEP_SECONDS", 2))

    def prompt(self, *, prompt: str, content: str, **kwargs: Any) -> EchoResponse:
        def response_iterator() -> Generator[str, None, None]:
            response = ["This", "is", "an", "echo", "backend:"]
            response += content.split()
            for word in response:
                if self.max_word_sleep_seconds > 0:
                    time.sleep(
                        random.random()
                        * random.randint(
                            self.min_word_sleep_seconds, self.max_word_sleep_seconds
                        )
                    )
                yield word

        return EchoResponse(response_iterator())
