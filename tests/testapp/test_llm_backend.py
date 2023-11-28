import os
import re

import pytest
from test_utils.settings import custom_ai_backend_class, custom_ai_backend_settings
from wagtail_ai.ai import InvalidAIBackendError, get_ai_backend

try:
    import llm  # noqa: F401
except ImportError:
    llm_installed = False
else:
    llm_installed = True


skip_if_llm_not_installed = pytest.mark.skipif(
    not llm_installed, reason="Requires llm to be installed."
)
skip_if_llm_installed = pytest.mark.skipif(
    llm_installed, reason="Requires llm to be not installed."
)


@pytest.fixture
def llm_backend_class():
    from wagtail_ai.ai.llm import LLMBackend

    return LLMBackend


@skip_if_llm_installed
@custom_ai_backend_class("wagtail_ai.ai.llm.LLMBackend")
def test_import_error():
    with pytest.raises(
        InvalidAIBackendError,
        match=re.escape(
            'Invalid AI backend: "AI backend "default" settings: "CLASS" '
            '("wagtail_ai.ai.llm.LLMBackend") is not importable.'
        ),
    ):
        get_ai_backend("default")


@skip_if_llm_not_installed
@custom_ai_backend_class("wagtail_ai.ai.llm.LLMBackend")
def test_get_configured_backend_instance(llm_backend_class):
    backend = get_ai_backend("default")
    assert isinstance(backend, llm_backend_class)


@skip_if_llm_not_installed
@custom_ai_backend_settings(
    new_value={
        "CLASS": "wagtail_ai.ai.llm.LLMBackend",
        "CONFIG": {
            "MODEL_ID": "gpt-3.5-turbo",
            "INIT_KWARGS": {"key": "random-api-key"},  # type: ignore
        },
    }
)
def test_llm_custom_init_kwargs(llm_backend_class):
    backend = get_ai_backend("default")
    assert backend.config.model_id == "gpt-3.5-turbo"
    assert backend.config.token_limit == 4096
    assert backend.config.init_kwargs == {"key": "random-api-key"}
    llm_model = backend.get_llm_model()  # type: ignore
    assert llm_model.key == "random-api-key"


@skip_if_llm_not_installed
@custom_ai_backend_settings(
    new_value={
        "CLASS": "wagtail_ai.ai.llm.LLMBackend",
        "CONFIG": {
            "MODEL_ID": "gpt-3.5-turbo",
            "PROMPT_KWARGS": {  # type: ignore
                "system": "This is a test system prompt."
            },
        },
    }
)
def test_llm_prompt_with_custom_kwargs(mocker):
    backend = get_ai_backend("default")
    assert backend.config.prompt_kwargs == {"system": "This is a test system prompt."}
    prompt_mock = mocker.patch("wagtail_ai.ai.llm.llm.models.Model.prompt")
    backend.prompt_with_context(pre_prompt="test pre prompt", context="test context")
    prompt_mock.assert_called_once_with(
        os.linesep.join(["test pre prompt", "test context"]),
        system="This is a test system prompt.",
    )
