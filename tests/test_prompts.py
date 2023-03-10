import pytest

from django.core.exceptions import ImproperlyConfigured

from wagtail_ai import DEFAULT_PROMPTS
from wagtail_ai.prompts import get_prompt_by_id, get_prompts


def test_get_prompts_returns_default_prompts():
    prompts = get_prompts()
    assert len(prompts) == len(DEFAULT_PROMPTS)
    assert prompts[0].label == DEFAULT_PROMPTS[0]["label"]


def test_prompts_are_given_ids():
    prompts = get_prompts()
    assert prompts[0].id is not None


def test_get_prompt_by_id_returns_prompts_as_indexed():
    assert get_prompt_by_id(0).label == DEFAULT_PROMPTS[0]["label"]


def test_custom_prompt(settings):
    settings.WAGTAIL_AI_PROMPTS = [
        {
            "label": "Custom Prompt",
            "description": "This is a custom prompt",
            "prompt": "The prompt",
            "method": "append",
        }
    ]

    assert get_prompts()[0].label == "Custom Prompt"


def test_extending_prompts(settings):
    settings.WAGTAIL_AI_PROMPTS = DEFAULT_PROMPTS + [
        {
            "label": "Custom Prompt",
            "description": "This is a custom prompt",
            "prompt": "The prompt",
            "method": "append",
        }
    ]

    assert get_prompts()[-1].label == "Custom Prompt"


def test_invalid_prompt(settings):
    settings.WAGTAIL_AI_PROMPTS = [
        {
            "description": "This is a custom prompt",
            "prompt": "The prompt",
        }
    ]

    with pytest.raises(ImproperlyConfigured):
        assert get_prompts()


def test_invalid_setting_structure(settings):
    settings.WAGTAIL_AI_PROMPTS = {
        "label": "Custom Prompt",
        "description": "This is a custom prompt",
        "prompt": "The prompt",
        "method": "append",
    }

    with pytest.raises(ImproperlyConfigured):
        assert get_prompts()


def test_invalid_method(settings):
    settings.WAGTAIL_AI_PROMPTS = {
        "label": "Custom Prompt",
        "description": "This is a custom prompt",
        "prompt": "The prompt",
        "method": "foo",
    }

    with pytest.raises(ImproperlyConfigured):
        assert get_prompts()
