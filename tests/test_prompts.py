import pytest
from django.core.exceptions import ValidationError
from wagtail_ai.models import Prompt
from wagtail_ai.prompts import DEFAULT_PROMPTS
from wagtail_ai.wagtail_hooks import get_prompts

# Apply pytest.mark.django_db to all tests in this file
pytestmark = pytest.mark.django_db


def test_prompt_model(setup_prompt_object, test_prompt_values):
    assert setup_prompt_object.is_default_prompt() is False
    assert str(setup_prompt_object) == test_prompt_values["label"]
    assert setup_prompt_object.label == test_prompt_values["label"]
    assert setup_prompt_object.prompt_value == test_prompt_values["prompt"]
    assert setup_prompt_object.description == test_prompt_values["description"]
    assert setup_prompt_object.method == test_prompt_values["method"]


def test_get_prompts_returns_default_prompts():
    prompts = get_prompts()
    default_prompts_queryset = Prompt.objects.filter(
        default_prompt_id__isnull=False
    ).all()

    assert len(default_prompts_queryset) == len(DEFAULT_PROMPTS)
    assert len(prompts) == len(DEFAULT_PROMPTS)
    assert prompts[0]["label"] == DEFAULT_PROMPTS[0]["label"]
    assert prompts[0]["prompt"] == DEFAULT_PROMPTS[0]["prompt"]


def test_editing_default_prompts():
    prompts = get_prompts()
    assert prompts[0]["label"] == DEFAULT_PROMPTS[0]["label"]
    assert prompts[0]["prompt"] == DEFAULT_PROMPTS[0]["prompt"]

    default_prompt = Prompt.objects.get(
        default_prompt_id=DEFAULT_PROMPTS[0]["default_prompt_id"]
    )

    default_prompt.prompt = "New Prompt Text"
    default_prompt.save()
    assert default_prompt.prompt_value == "New Prompt Text"

    prompts = get_prompts()
    assert prompts[0]["prompt"] == "New Prompt Text"
    assert prompts[0]["prompt"] != DEFAULT_PROMPTS[0]["prompt"]


def test_get_prompts_returns_new_prompts_and_default_prompts(setup_prompt_object):
    prompts = get_prompts()
    assert (
        len(prompts) == len(DEFAULT_PROMPTS) + 1
    )  # 1 Prompt from setup_prompt_object is added

    # Check setup_prompt_object is in get_prompts
    assert setup_prompt_object.label in [prompt["label"] for prompt in prompts]
    assert setup_prompt_object.prompt in [prompt["prompt"] for prompt in prompts]

    # Check DEFAULT_PROMPTS are in get_prompts
    for prompt in DEFAULT_PROMPTS:
        assert prompt["label"] in [prompt["label"] for prompt in prompts]
        assert prompt["prompt"] in [prompt["prompt"] for prompt in prompts]


def test_prompts_return_uuids_and_not_ids():
    prompts = get_prompts()
    assert prompts[0]["uuid"] is not None
    assert "id" not in prompts[0]


def test_prompts_can_not_save_and_invalid_method(test_prompt_values):
    with pytest.raises(ValidationError):
        prompt = Prompt.objects.create(
            label=test_prompt_values["label"],
            description=test_prompt_values["description"],
            prompt=test_prompt_values["prompt"],
            method="foo",
        )
        prompt.full_clean()
