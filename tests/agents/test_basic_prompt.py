import json
from unittest.mock import MagicMock

import pytest
from django.http import HttpResponse
from django.urls import reverse
from django_ai_core.contrib.agents import registry

from wagtail_ai.agents.basic_prompt import BasicPromptAgent
from wagtail_ai.models import AgentSettings


def test_agent_configuration():
    assert BasicPromptAgent.slug == "wai_basic_prompt"
    assert BasicPromptAgent.parameters is not None
    assert len(BasicPromptAgent.parameters) == 2
    param_names = [(param.name, param.type) for param in BasicPromptAgent.parameters]

    assert param_names == [
        ("prompt", str),
        ("context", dict[str, str]),
    ]

    assert BasicPromptAgent.provider_alias == "default"

    # Ensure the agent is registered with django-ai-core
    assert registry.get(BasicPromptAgent.slug) is BasicPromptAgent

    # And the view is registered with Wagtail
    assert reverse("wagtail_ai:basic_prompt") == "/admin/ai/basic_prompt/"


def test_settings_prompts():
    """Verify that the agent has the expected settings prompts."""
    assert len(BasicPromptAgent.settings_prompts) == 5
    prompt_names = [p.name for p in BasicPromptAgent.settings_prompts]
    assert prompt_names == [
        "page_title_prompt",
        "page_description_prompt",
        "image_title_prompt",
        "image_description_prompt",
        "contextual_alt_text_prompt",
    ]


@pytest.fixture
def mock_llm_service(monkeypatch):
    """Mock the get_llm_service function to return a mock service."""
    mock_completion = MagicMock()
    mock_completion.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Generated content from AI"))]
    )

    mock_service = MagicMock()
    mock_service.completion = mock_completion

    def mock_get_llm_service(alias):
        mock_service.alias = alias
        return mock_service

    monkeypatch.setattr(
        "wagtail_ai.agents.basic_prompt.get_llm_service",
        mock_get_llm_service,
    )

    return mock_service


@pytest.mark.django_db
def test_page_title_prompt(admin_client, mock_llm_service):
    """Test generating a page title with the default prompt."""
    settings = AgentSettings.load()
    settings.save()

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:basic_prompt"),
        data=json.dumps(
            {
                "arguments": {
                    "prompt": settings.page_title_prompt,
                    "context": {
                        "content_html": "<p>This is some page content about AI.</p>"
                    },
                }
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
    content = json.loads(response.content.decode())

    mock_llm_service.completion.assert_called_once()
    messages = mock_llm_service.completion.call_args.kwargs["messages"]

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert "content" in messages[0]
    assert len(messages[0]["content"]) == 1
    assert messages[0]["content"][0]["type"] == "text"
    assert "Create an SEO-friendly page title" in messages[0]["content"][0]["text"]
    assert "This is some page content about AI" in messages[0]["content"][0]["text"]

    assert content["status"] == "completed"
    assert content["data"] == "Generated content from AI"


@pytest.mark.django_db
def test_page_description_prompt(admin_client, mock_llm_service):
    """Test generating a page description with the default prompt."""
    settings = AgentSettings.load()
    settings.save()

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:basic_prompt"),
        data=json.dumps(
            {
                "arguments": {
                    "prompt": settings.page_description_prompt,
                    "context": {
                        "content_html": "<p>This is some page content about AI.</p>"
                    },
                }
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
    content = json.loads(response.content.decode())

    mock_llm_service.completion.assert_called_once()
    messages = mock_llm_service.completion.call_args.kwargs["messages"]

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert (
        "Create an SEO-friendly meta description" in messages[0]["content"][0]["text"]
    )
    assert "This is some page content about AI" in messages[0]["content"][0]["text"]

    assert content["status"] == "completed"
    assert content["data"] == "Generated content from AI"


@pytest.mark.django_db
def test_image_title_prompt(admin_client, mock_llm_service, settings, image_data_url):
    """Test generating an image title with a data URL image."""
    agent_settings = AgentSettings.load()

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:basic_prompt"),
        data=json.dumps(
            {
                "arguments": {
                    "prompt": agent_settings.image_title_prompt,
                    "context": {
                        "image": image_data_url,
                        "max_length": "100",
                    },
                }
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
    content = json.loads(response.content.decode())

    mock_llm_service.completion.assert_called_once()
    messages = mock_llm_service.completion.call_args.kwargs["messages"]

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    # Check that the message contains both text and image_url
    assert len(messages[0]["content"]) == 2
    assert messages[0]["content"][0]["type"] == "text"
    assert "Generate a title" in messages[0]["content"][0]["text"]
    assert "100 characters" in messages[0]["content"][0]["text"]
    assert "[file 1]" in messages[0]["content"][0]["text"]

    assert messages[0]["content"][1]["type"] == "image_url"
    assert messages[0]["content"][1]["image_url"]["url"] == image_data_url

    assert content["status"] == "completed"
    assert content["data"] == "Generated content from AI"


@pytest.mark.django_db
def test_image_description_prompt(
    admin_client, mock_llm_service, settings, image_data_url
):
    """Test generating an image description with a data URL image."""
    agent_settings = AgentSettings.load()

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:basic_prompt"),
        data=json.dumps(
            {
                "arguments": {
                    "prompt": agent_settings.image_description_prompt,
                    "context": {
                        "image": image_data_url,
                        "max_length": "255",
                    },
                }
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
    content = json.loads(response.content.decode())

    mock_llm_service.completion.assert_called_once()
    messages = mock_llm_service.completion.call_args.kwargs["messages"]

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert len(messages[0]["content"]) == 2
    assert messages[0]["content"][0]["type"] == "text"
    assert "Generate a description" in messages[0]["content"][0]["text"]
    assert "255 characters" in messages[0]["content"][0]["text"]

    assert messages[0]["content"][1]["type"] == "image_url"

    assert content["status"] == "completed"
    assert content["data"] == "Generated content from AI"


@pytest.mark.django_db
def test_contextual_alt_text_prompt(
    admin_client, mock_llm_service, settings, image_data_url
):
    """Test generating contextual alt text with image and context."""
    agent_settings = AgentSettings.load()

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:basic_prompt"),
        data=json.dumps(
            {
                "arguments": {
                    "prompt": agent_settings.contextual_alt_text_prompt,
                    "context": {
                        "image": image_data_url,
                        "form_context_before": "This is the content before the image.",
                        "form_context_after": "This is the content after the image.",
                    },
                }
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
    content = json.loads(response.content.decode())

    mock_llm_service.completion.assert_called_once()
    messages = mock_llm_service.completion.call_args.kwargs["messages"]

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert len(messages[0]["content"]) == 2

    # Verify the prompt contains the context
    prompt_text = messages[0]["content"][0]["text"]
    assert "Generate an alt text" in prompt_text
    assert "[file 1]" in prompt_text
    assert "This is the content before the image" in prompt_text
    assert "This is the content after the image" in prompt_text

    # Verify image is passed
    assert messages[0]["content"][1]["type"] == "image_url"

    assert content["status"] == "completed"
    assert content["data"] == "Generated content from AI"


@pytest.mark.django_db
def test_custom_prompt(admin_client, mock_llm_service):
    """Test with a custom prompt that's not from settings."""
    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:basic_prompt"),
        data=json.dumps(
            {
                "arguments": {
                    "prompt": "Summarize this in one word: {text}",
                    "context": {"text": "The quick brown fox jumps over the lazy dog."},
                }
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
    content = json.loads(response.content.decode())

    mock_llm_service.completion.assert_called_once()
    messages = mock_llm_service.completion.call_args.kwargs["messages"]

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert len(messages[0]["content"]) == 1
    assert (
        "Summarize this in one word: The quick brown fox jumps over the lazy dog."
        == messages[0]["content"][0]["text"]
    )

    assert content["status"] == "completed"
    assert content["data"] == "Generated content from AI"


@pytest.mark.django_db
def test_provider_alias_for_image_description(
    admin_client, mock_llm_service, settings, image_data_url
):
    """Test that IMAGE_DESCRIPTION_PROVIDER is used when context contains an image."""
    settings.WAGTAIL_AI = {
        "IMAGE_DESCRIPTION_PROVIDER": "custom_provider",
    }

    agent_settings = AgentSettings.load()

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:basic_prompt"),
        data=json.dumps(
            {
                "arguments": {
                    "prompt": agent_settings.image_title_prompt,
                    "context": {
                        "image": image_data_url,
                        "max_length": "100",
                    },
                }
            }
        ),
        content_type="application/json",
    )

    assert response.status_code == 200

    # Verify that get_llm_service was called with the custom provider
    mock_llm_service.completion.assert_called_once()
    assert mock_llm_service.alias == "custom_provider"
