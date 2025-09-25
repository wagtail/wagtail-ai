import base64
from typing import cast
from unittest.mock import ANY, Mock
from urllib.parse import urlsplit

import pytest
from wagtail.images.models import Image
from wagtail_factories import ImageFactory

from wagtail_ai.ai import get_ai_backend, get_backend
from wagtail_ai.ai.base import BackendFeature
from wagtail_ai.ai.openai import OpenAIBackend

pytestmark = pytest.mark.django_db

MOCK_API_KEY = "openai-api-key-stub"
MOCK_OUTPUT = "mock ai output"


@pytest.fixture(autouse=True)
def stub_image_title_signal(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENAI_API_KEY", MOCK_API_KEY)


@pytest.fixture
def mock_post(monkeypatch: pytest.MonkeyPatch):
    mock = Mock()
    monkeypatch.setattr("requests.post", mock)
    return mock


def test_get_as_image_backend(settings):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "openai": {
                "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
                "CONFIG": {
                    "MODEL_ID": "mock model",
                    "TOKEN_LIMIT": 123123,
                    "TIMEOUT_SECONDS": 321,
                },
            },
        },
        "IMAGE_DESCRIPTION_BACKEND": "openai",
    }

    backend = get_backend(BackendFeature.IMAGE_DESCRIPTION)
    assert isinstance(backend, OpenAIBackend)
    assert backend.config.model_id == "mock model"
    assert backend.config.token_limit == 123123
    assert backend.config.timeout_seconds == 321


def test_describe_image(settings, mock_post):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "openai": {
                "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-4",
                },
            },
        },
    }

    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": MOCK_OUTPUT}}],
    }
    image = cast(Image, ImageFactory())
    backend = get_ai_backend("openai")
    prompt = "what do you see?"

    response = backend.describe_image(image_file=image.file, prompt=prompt)
    assert response.text() == MOCK_OUTPUT

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["Authorization"] == f"Bearer {MOCK_API_KEY}"

    messages = mock_post.call_args.kwargs["json"]["messages"]
    assert messages == [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": ANY}},
            ],
        }
    ]
    url = messages[0]["content"][1]["image_url"]["url"]
    assert url.startswith("data:image/jpeg;base64,")


def test_prompt(settings, mock_post, image_data_url):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "openai": {
                "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-4",
                },
            },
        },
    }

    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": MOCK_OUTPUT}}],
    }
    backend = get_ai_backend("openai")
    image = cast(Image, ImageFactory())

    context = {
        "name": "Gordon",
        "image": image.file,
        "id_card": urlsplit(image_data_url),
    }
    with image.file.open("rb") as f:
        content = base64.b64encode(f.read()).decode()

    response = backend.prompt(
        prompt=(
            "My name is {name}. Here's my photo: {image}. "
            "Here's a scan of my ID card: {id_card}"
        ),
        context=context,
    )
    assert context["image"] == "[file 1]"
    assert "".join(response) == MOCK_OUTPUT
    assert response.text() == MOCK_OUTPUT

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["Authorization"] == f"Bearer {MOCK_API_KEY}"

    messages = mock_post.call_args.kwargs["json"]["messages"]
    assert messages == [
        {
            "content": [
                {
                    "type": "text",
                    "text": (
                        "My name is Gordon. Here's my photo: [file 1]. "
                        "Here's a scan of my ID card: [file 2]"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{content}"},
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_data_url},
                },
            ],
            "role": "user",
        },
    ]


def test_text_completion(settings, mock_post):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "openai": {
                "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-4",
                },
            },
        },
    }

    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": MOCK_OUTPUT}}],
    }
    backend = get_ai_backend("openai")
    pre_prompt = "You are assisting the user in testing the code."
    context = "Some mock content."
    post_prompt = "What just happened?"

    response = backend.prompt_with_context(
        pre_prompt=pre_prompt, context=context, post_prompt=post_prompt
    )
    assert "".join(response) == MOCK_OUTPUT
    assert response.text() == MOCK_OUTPUT

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["Authorization"] == f"Bearer {MOCK_API_KEY}"

    messages = mock_post.call_args.kwargs["json"]["messages"]
    assert messages == [
        {"content": [{"type": "text", "text": pre_prompt}], "role": "system"},
        {"content": [{"type": "text", "text": context}], "role": "user"},
        {"content": [{"type": "text", "text": post_prompt}], "role": "system"},
    ]


def test_text_completion_without_post_prompt(settings, mock_post):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "openai": {
                "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-4",
                },
            },
        },
    }

    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": MOCK_OUTPUT}}],
    }
    backend = get_ai_backend("openai")
    pre_prompt = "You are assisting the user in testing the code."
    context = "Some mock content."

    response = backend.prompt_with_context(pre_prompt=pre_prompt, context=context)
    assert response.text() == MOCK_OUTPUT

    messages = mock_post.call_args.kwargs["json"]["messages"]
    assert messages == [
        {"content": [{"type": "text", "text": pre_prompt}], "role": "system"},
        {"content": [{"type": "text", "text": context}], "role": "user"},
    ]


def test_default_token_limit(settings):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "openai": {
                "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-4",
                },
            },
        },
    }

    backend = get_ai_backend("openai")
    assert backend.config.token_limit == 8192


def test_api_key_in_environ(settings, monkeypatch: pytest.MonkeyPatch):
    test_key = "test-key-value"
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "openai": {
                "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-4",
                },
            },
        },
    }
    monkeypatch.setenv("OPENAI_API_KEY", test_key)

    backend = cast(OpenAIBackend, get_ai_backend("openai"))
    assert backend.get_openai_api_key() == test_key


def test_api_key_in_settings(settings):
    test_key = "test-key-value"
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "openai": {
                "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-4",
                    "OPENAI_API_KEY": test_key,
                },
            },
        },
    }

    backend = cast(OpenAIBackend, get_ai_backend("openai"))
    assert backend.get_openai_api_key() == test_key
