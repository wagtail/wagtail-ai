from typing import cast
from unittest.mock import ANY, Mock

import pytest
from wagtail.images.models import Image
from wagtail_ai.ai.openai import OpenAIBackend
from wagtail_factories import ImageFactory

pytestmark = pytest.mark.django_db

MOCK_API_KEY = "MOCK-API-KEY"


@pytest.fixture(autouse=True)
def stub_image_title_signal(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "wagtail_ai.ai.openai.OpenAIBackend.get_openai_api_key",
        lambda self: MOCK_API_KEY,
    )


@pytest.fixture
def mock_post(monkeypatch: pytest.MonkeyPatch):
    mock = Mock()
    monkeypatch.setattr("requests.post", mock)
    return mock


def test_describe_image(mock_post):
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "nothing"}}],
    }
    image = cast(Image, ImageFactory())
    backend = OpenAIBackend()
    prompt = "what do you see?"

    description = backend.describe_image(image_file=image.file, prompt=prompt)
    assert description == "nothing"

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
