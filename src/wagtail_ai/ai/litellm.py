import base64
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, NotRequired, Self

from django.core.files import File

from wagtail_ai.types import AIResponse

from .base import AIBackend, BaseAIBackendConfig, BaseAIBackendConfigSettings


class LiteLLMBackendConfigSettingsDict(BaseAIBackendConfigSettings):
    TIMEOUT_SECONDS: NotRequired[int | None]
    API_KEY: NotRequired[str | None]
    API_BASE: NotRequired[str | None]


@dataclass(kw_only=True)
class LiteLLMBackendConfig(BaseAIBackendConfig[LiteLLMBackendConfigSettingsDict]):
    timeout_seconds: int
    api_key: str | None
    api_base: str | None

    @classmethod
    def from_settings(
        cls, config: LiteLLMBackendConfigSettingsDict, **kwargs: Any
    ) -> Self:
        timeout_seconds = config.get("TIMEOUT_SECONDS")
        if timeout_seconds is None:
            timeout_seconds = 30
        kwargs.setdefault("timeout_seconds", timeout_seconds)
        kwargs.setdefault("api_key", config.get("API_KEY"))
        kwargs.setdefault("api_base", config.get("API_BASE"))

        return super().from_settings(config, **kwargs)


class LiteLLMResponse(AIResponse):
    def __init__(self, text: str):
        self._text = text

    def __iter__(self) -> Iterator[str]:
        yield self._text

    def text(self) -> str:
        return self._text

    def __str__(self):
        return self.text()


class LiteLLMBackend(AIBackend[LiteLLMBackendConfig]):
    config_cls = LiteLLMBackendConfig

    def prompt_with_context(
        self, *, pre_prompt: str, context: str, post_prompt: str | None = None
    ) -> LiteLLMResponse:
        messages = [
            {"role": "system", "content": [{"type": "text", "text": pre_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": context}]},
        ]

        if post_prompt is not None:
            messages.append(
                {"role": "system", "content": [{"type": "text", "text": post_prompt}]}
            )

        return self._completion(messages)

    def describe_image(self, *, image_file: File, prompt: str) -> LiteLLMResponse:
        if not prompt:
            raise ValueError("Prompt must not be empty.")
        with image_file.open() as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        return self._completion(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
        )

    def _completion(self, messages: list[dict[str, Any]]) -> LiteLLMResponse:
        import litellm

        kwargs: dict[str, Any] = {
            "model": self.config.model_id,
            "messages": messages,
            "max_tokens": self.config.token_limit,
            "timeout": self.config.timeout_seconds,
            "drop_params": True,
        }
        if self.config.api_key:
            kwargs["api_key"] = self.config.api_key
        if self.config.api_base:
            kwargs["api_base"] = self.config.api_base

        response = litellm.completion(**kwargs)
        text = response.choices[0].message.content or ""
        return LiteLLMResponse(text)
