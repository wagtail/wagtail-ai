import base64
import os

import requests
from django.core.files import File

from .base import DescribeImageBackend, DescribeImageError


class DescribeImageOpenAI(DescribeImageBackend):
    timeout_seconds: int | None = None
    openai_api_key: str | None = None

    def __init__(
        self, *, timeout_seconds: int | None = 15, openai_api_key: str | None = None
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.openai_api_key = openai_api_key

    def describe_image(self, *, image_file: File, prompt: str) -> str:
        if not prompt:
            raise ValueError("Prompt must not be empty.")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_openai_api_key()}",
        }
        with image_file.open() as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
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
                }
            ],
            "max_tokens": 300,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout_seconds,
        )

        try:
            response.raise_for_status()
            json_response = response.json()
        except requests.RequestException as e:
            raise DescribeImageError(e) from e

        try:
            return json_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise DescribeImageError(e) from e

    def get_openai_api_key(self) -> str:
        if self.openai_api_key is not None:
            return self.openai_api_key
        env_key = os.environ.get("OPENAI_API_KEY")
        if env_key is None:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
        return env_key
