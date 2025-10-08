import random
import time
from collections.abc import Generator, Iterator
from dataclasses import dataclass
from typing import Any, NotRequired, Self

from django.core.exceptions import ImproperlyConfigured
from django.core.files import File

from .base import (
    AIBackend,
    AIResponse,
    BaseAIBackendConfig,
    BaseAIBackendConfigSettings,
)


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


@dataclass(kw_only=True)
class EchoBackendSettingsDict(BaseAIBackendConfigSettings):
    MAX_WORD_SLEEP_SECONDS: NotRequired[int]


@dataclass(kw_only=True)
class EchoBackendConfig(BaseAIBackendConfig[EchoBackendSettingsDict]):
    max_word_sleep_seconds: int

    @classmethod
    def from_settings(cls, config: EchoBackendSettingsDict, **kwargs: Any) -> Self:
        max_word_sleep_seconds = config.get("MAX_WORD_SLEEP_SECONDS")
        if max_word_sleep_seconds is None:
            max_word_sleep_seconds = 0
        try:
            max_word_sleep_seconds = int(max_word_sleep_seconds)
        except ValueError as e:
            raise ImproperlyConfigured(
                f'"MAX_WORD_SLEEP_SECONDS" is not an "int", it is a "{type(max_word_sleep_seconds)}".'
            ) from e
        kwargs.setdefault("max_word_sleep_seconds", max_word_sleep_seconds)

        return super().from_settings(config, **kwargs)


class EchoBackend(AIBackend[EchoBackendConfig]):
    config_cls = EchoBackendConfig

    def prompt_with_context(
        self, *, pre_prompt: str, context: str, post_prompt: str | None = None
    ) -> AIResponse:
        return self.get_response(
            ["This", "is", "an", "echo", "backend:", *context.split()]
        )

    def describe_image(self, *, image_file: File, prompt: str) -> AIResponse:
        return self.get_response(
            ["This", "is", "an", "echo", "backend:", image_file.name]
        )

    def get_response(self, words):
        def response_iterator() -> Generator[str, None, None]:
            for word in words:
                if (
                    self.config.max_word_sleep_seconds is not None
                    and self.config.max_word_sleep_seconds > 0
                ):
                    time.sleep(
                        random.random()
                        * random.randint(0, self.config.max_word_sleep_seconds)
                    )
                yield word

        return EchoResponse(response_iterator())
