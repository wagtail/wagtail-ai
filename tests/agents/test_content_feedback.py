import json
from unittest.mock import MagicMock

import pytest
from django.http import HttpResponse
from django.urls import reverse
from django_ai_core.contrib.agents import registry

from wagtail_ai.agents.content_feedback import ContentFeedbackAgent
from wagtail_ai.models import AgentSettings


def test_agent_configuration():
    assert ContentFeedbackAgent.slug == "wai_content_feedback"
    assert ContentFeedbackAgent.parameters is not None
    assert len(ContentFeedbackAgent.parameters) == 4
    param_names = [
        (param.name, param.type) for param in ContentFeedbackAgent.parameters
    ]

    assert param_names == [
        ("content_text", str),
        ("content_html", str),
        ("content_language", str),
        ("editor_language", str),
    ]

    assert ContentFeedbackAgent.provider_alias == "default"

    # Ensure the agent is registered with django-ai-core
    assert registry.get(ContentFeedbackAgent.slug) is ContentFeedbackAgent

    # And the view is registered with Wagtail
    assert reverse("wagtail_ai:content_feedback") == "/admin/ai/content_feedback/"


@pytest.fixture
def mock_result():
    return {
        "quality_score": 2,
        "qualitative_feedback": [
            "Strength 1",
            "Strength 2",
            "Strength 3",
        ],
        "specific_improvements": [
            {
                "original_text": "foo",
                "suggested_text": "bar",
                "explanation": "baz",
            }
        ],
    }


@pytest.fixture
def mock_llm_service(monkeypatch, mock_result):
    """Mock the get_llm_service function to return a mock service."""
    mock_completion = MagicMock()
    mock_completion.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=json.dumps(mock_result)))]
    )

    mock_service = MagicMock()
    mock_service.completion = mock_completion

    def mock_get_llm_service(alias):
        return mock_service

    monkeypatch.setattr(
        "wagtail_ai.agents.content_feedback.get_llm_service",
        mock_get_llm_service,
    )

    return mock_service


@pytest.mark.django_db
def test_prompt_with_plain_text_and_no_custom_prompt(
    admin_client, mock_llm_service, mock_result
):
    settings = AgentSettings.load()
    settings.content_feedback_content_type = settings.ContentFeedbackContentType.TEXT
    settings.save()

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:content_feedback"),
        data=json.dumps(
            {
                "arguments": {
                    "content_text": "Some content",
                    "content_html": "<p>Some content</p>",
                    "content_language": "American English",
                    "editor_language": "British English",
                }
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    content = json.loads(response.content.decode())

    mock_llm_service.completion.assert_called_once()
    messages = mock_llm_service.completion.call_args.kwargs["messages"]

    assert len(messages) == 3
    assert messages[2]["content"] == "Content to review:\n\nSome content"
    assert content["status"] == "completed"
    assert content["data"] == mock_result


@pytest.mark.django_db
def test_prompt_with_html_and_custom_prompt(
    admin_client, mock_llm_service, mock_result
):
    settings = AgentSettings.load()
    settings.content_feedback_prompt = "Content must include the word 'bird'."
    settings.save()

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:content_feedback"),
        data=json.dumps(
            {
                "arguments": {
                    "content_text": "Some content",
                    "content_html": "<p>Some content</p>",
                    "content_language": "English",
                    "editor_language": "French",
                }
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    content = json.loads(response.content.decode())

    mock_llm_service.completion.assert_called_once()
    messages = mock_llm_service.completion.call_args.kwargs["messages"]

    assert len(messages) == 4
    assert messages[2] == {
        "role": "user",
        "content": "Content must include the word 'bird'.",
    }
    assert messages[3]["content"] == "Content to review:\n\n<p>Some content</p>"
    assert content["status"] == "completed"
    assert content["data"] == mock_result
