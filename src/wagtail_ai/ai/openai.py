import base64
import os
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, NotRequired, Self

import requests
from django.core.files import File

from wagtail_ai.types import AIResponse

from .base import AIBackend, BaseAIBackendConfig, BaseAIBackendConfigSettings


class OpenAIBackendConfigSettingsDict(BaseAIBackendConfigSettings):
    TIMEOUT_SECONDS: NotRequired[int | None]
    OPENAI_API_KEY: NotRequired[str | None]


@dataclass(kw_only=True)
class OpenAIBackendConfig(BaseAIBackendConfig[OpenAIBackendConfigSettingsDict]):
    timeout_seconds: int
    openai_api_key: str | None

    @classmethod
    def from_settings(
        cls, config: OpenAIBackendConfigSettingsDict, **kwargs: Any
    ) -> Self:
        timeout_seconds = config.get("TIMEOUT_SECONDS")
        if timeout_seconds is None:
            timeout_seconds = 15
        kwargs.setdefault("timeout_seconds", timeout_seconds)

        kwargs.setdefault("openai_api_key", config.get("OPENAI_API_KEY"))

        return super().from_settings(config, **kwargs)


class OpenAIResponse(AIResponse):
    def __init__(self, response: requests.Response):
        self.response = response
        self._text = response.json()["choices"][0]["message"]["content"]

    def __iter__(self) -> Iterator[str]:
        yield self._text

    def text(self) -> str:
        return self._text

    def __str__(self):
        return self.text()


class OpenAIBackend(AIBackend[OpenAIBackendConfig]):
    config_cls = OpenAIBackendConfig

    def prompt_with_context(
        self, *, pre_prompt: str, context: str, post_prompt: str | None = None
    ) -> OpenAIResponse:
        messages = [
            {"role": "system", "content": [{"type": "text", "text": pre_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": context}]},
        ]

        if post_prompt is not None:
            messages.append(
                {"role": "system", "content": [{"type": "text", "text": post_prompt}]}
            )

        return self.chat_completions(messages)

    def describe_image(self, *, image_file: File, prompt: str) -> OpenAIResponse:
        if not prompt:
            raise ValueError("Prompt must not be empty.")
        with image_file.open() as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        return self.chat_completions(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
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

    def chat_completions(self, messages: list[dict[str, Any]]) -> OpenAIResponse:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_openai_api_key()}",
        }
        payload = {
            "model": self.config.model_id,
            "messages": messages,
            "max_tokens": self.config.token_limit,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.config.timeout_seconds,
        )

        response.raise_for_status()
        return OpenAIResponse(response)

    def get_openai_api_key(self) -> str:
        if config_key := self.config.openai_api_key:
            return config_key

        if env_key := os.environ.get("OPENAI_API_KEY"):
            return env_key

        raise RuntimeError(
            "Cannot find OpenAI API key. Please set the OPENAI_API_KEY environment"
            " variable or the OPENAI_API_KEY backend config value in Django settings."
        )
