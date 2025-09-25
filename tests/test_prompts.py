import pytest
from django.core.exceptions import ValidationError

from wagtail_ai.models import Prompt
from wagtail_ai.prompts import DEFAULT_PROMPTS
from wagtail_ai.wagtail_hooks import get_prompts


@pytest.mark.django_db
def test_prompt_model(setup_prompt_object, test_prompt_values):
    assert setup_prompt_object.is_default is False
    assert str(setup_prompt_object) == test_prompt_values["label"]
    assert setup_prompt_object.label == test_prompt_values["label"]
    assert setup_prompt_object.prompt_value == test_prompt_values["prompt"]
    assert setup_prompt_object.description == test_prompt_values["description"]
    assert setup_prompt_object.method == test_prompt_values["method"]


@pytest.mark.django_db
def test_get_prompts_returns_default_prompts():
    prompts = get_prompts()

    assert {(p["label"], p["prompt"]) for p in prompts} == {
        (p["label"], p["prompt"]) for p in DEFAULT_PROMPTS
    }


def find_prompt_by_label(prompts, label):
    return next((prompt for prompt in prompts if prompt["label"] == label), None)


@pytest.mark.django_db
def test_editing_default_prompts():
    # Get a default prompt and check it's returned by get_prompts
    prompts = get_prompts()
    default_prompt = Prompt.objects.get(
        default_prompt_id=DEFAULT_PROMPTS[0]["default_prompt_id"]
    )
    prompt_from_get_prompts = find_prompt_by_label(prompts, default_prompt.label)
    assert prompt_from_get_prompts is not None

    # Check the prompt value is the same as the default prompt value
    assert default_prompt.prompt is None
    assert prompt_from_get_prompts["prompt"] == default_prompt.prompt_value

    # Saving an empty string should return the default prompt value
    default_prompt.prompt = ""
    default_prompt.save()
    assert default_prompt.prompt_value == DEFAULT_PROMPTS[0]["prompt"]

    # Add a prompt value to the default prompt
    default_prompt.prompt = "New Prompt Text"
    default_prompt.save()
    assert default_prompt.prompt_value == "New Prompt Text"

    # Check the updated prompt value is returned by get_prompts
    prompts = get_prompts()
    prompt_from_get_prompts = find_prompt_by_label(prompts, default_prompt.label)
    assert prompt_from_get_prompts is not None
    assert prompt_from_get_prompts["prompt"] == default_prompt.prompt_value
    assert prompt_from_get_prompts["prompt"] == default_prompt.prompt


@pytest.mark.django_db
def test_get_prompts_returns_new_prompts_and_default_prompts(setup_prompt_object):
    prompt_object = setup_prompt_object
    prompts = get_prompts()
    assert {p["label"] for p in prompts} == set(
        [p["label"] for p in DEFAULT_PROMPTS] + [prompt_object.label]
    )

    # Check setup_prompt_object is in get_prompts
    assert setup_prompt_object.label in [prompt["label"] for prompt in prompts]
    assert setup_prompt_object.prompt in [prompt["prompt"] for prompt in prompts]

    # Check DEFAULT_PROMPTS are in get_prompts
    for prompt in DEFAULT_PROMPTS:
        assert prompt["label"] in [prompt["label"] for prompt in prompts]
        assert prompt["prompt"] in [prompt["prompt"] for prompt in prompts]


@pytest.mark.django_db
def test_prompts_return_uuids_and_not_ids():
    prompts = get_prompts()
    assert prompts[0]["uuid"] is not None
    assert "id" not in prompts[0]


@pytest.mark.django_db
def test_prompts_can_not_save_and_invalid_method(test_prompt_values):
    with pytest.raises(ValidationError, match="Value 'foo' is not a valid choice."):
        prompt = Prompt(
            label=test_prompt_values["label"],
            description=test_prompt_values["description"],
            prompt=test_prompt_values["prompt"],
            method="foo",
        )
        prompt.full_clean()
