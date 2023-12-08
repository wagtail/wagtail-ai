import pytest
from django.contrib.auth.models import User
from wagtail_ai.models import Prompt

TEST_PROMPT_LABEL = "Prompt Label"
TEST_PROMPT_VALUE = "Prompt Text"
TEST_PROMPT_DESCRIPTION = "Prompt Text"


@pytest.fixture
def test_prompt_values():
    return {
        "label": TEST_PROMPT_LABEL,
        "description": TEST_PROMPT_DESCRIPTION,
        "prompt": TEST_PROMPT_VALUE,
        "method": Prompt.Method.REPLACE.value,
    }


@pytest.fixture
def setup_prompt_object(test_prompt_values):
    prompt = Prompt.objects.create(**test_prompt_values)

    yield prompt

    prompt.delete()


@pytest.fixture
def setup_users():
    superuser = User.objects.create_superuser(
        "Superuser", "superuser@email.com", "password"
    )

    yield superuser

    superuser.delete()
