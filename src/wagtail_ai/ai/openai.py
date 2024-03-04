import base64
import os
from dataclasses import dataclass
from typing import Any, NotRequired, Self

import requests
from django.core.files import File

from .base import AIBackend, BaseAIBackendConfig, BaseAIBackendConfigSettings


class OpenAIBackendConfigSettingsDict(BaseAIBackendConfigSettings):
    TIMEOUT_SECONDS: NotRequired[int | None]


@dataclass(kw_only=True)
class OpenAIBackendConfig(BaseAIBackendConfig[OpenAIBackendConfigSettingsDict]):
    timeout_seconds: int

    @classmethod
    def from_settings(
        cls, config: OpenAIBackendConfigSettingsDict, **kwargs: Any
    ) -> Self:
        timeout_seconds = config.get("TIMEOUT_SECONDS")
        if timeout_seconds is None:
            timeout_seconds = 15
        kwargs.setdefault("timeout_seconds", timeout_seconds)

        return super().from_settings(config, **kwargs)


class OpenAIBackend(AIBackend[OpenAIBackendConfig]):
    config_cls = OpenAIBackendConfig

    def describe_image(self, *, image_file: File, prompt: str) -> str:
        if not prompt:
            raise ValueError("Prompt must not be empty.")
        with image_file.open() as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        response = self.chat_completions(
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
        return response["choices"][0]["message"]["content"]

    def chat_completions(self, messages: list[dict[str, Any]]):
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
        return response.json()

    def get_openai_api_key(self) -> str:
        env_key = os.environ.get("OPENAI_API_KEY")
        if env_key is None:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
        return env_key
