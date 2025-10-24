import re

import pytest
from test_utils.settings import (
    custom_ai_backend_class,
    custom_ai_backend_settings,
)

from wagtail_ai.ai import (
    BackendNotFound,
    InvalidAIBackendError,
    get_ai_backend,
    get_backend,
)
from wagtail_ai.ai.base import BackendFeature
from wagtail_ai.ai.echo import EchoBackend


@custom_ai_backend_class("wagtail_ai.ai.echo.EchoBackend")
def test_get_configured_backend_instance() -> None:
    backend = get_ai_backend("default")
    assert isinstance(backend, EchoBackend)


@custom_ai_backend_class("some.random.not.existing.path")
def test_get_invalid_backend_class_instance() -> None:
    with pytest.raises(
        InvalidAIBackendError,
        match=re.escape(
            'Invalid AI backend: "AI backend "default" settings: "CLASS" '
            '("some.random.not.existing.path") is not importable.'
        ),
    ):
        get_ai_backend("default")


@custom_ai_backend_settings(
    new_value={
        "CLASS": "wagtail_ai.ai.echo.EchoBackend",
        "CONFIG": {
            "MODEL_ID": "echo",
            "TOKEN_LIMIT": 123123,
            "MAX_WORD_SLEEP_SECONDS": 150,  # type: ignore
        },
    }
)
def test_get_backend_instance_with_custom_setting() -> None:
    backend = get_ai_backend("default")
    assert isinstance(backend, EchoBackend)
    assert backend.config.model_id == "echo"
    assert backend.config.max_word_sleep_seconds == 150
    assert backend.config.token_limit == 123123


@custom_ai_backend_settings(
    new_value={
        "CLASS": "wagtail_ai.ai.echo.EchoBackend",
        "CONFIG": {
            "MODEL_ID": "echo",
            "TOKEN_LIMIT": 123123,
            "MAX_WORD_SLEEP_SECONDS": 0,  # type: ignore
        },
    }
)
def test_prompt_with_context() -> None:
    backend = get_ai_backend("default")
    response = backend.prompt_with_context(
        pre_prompt="Translate the following context to French.",
        context="I like trains.",
    )
    assert response.text() == "This is an echo backend: I like trains."


@custom_ai_backend_settings(
    new_value={
        "CLASS": "wagtail_ai.ai.echo.EchoBackend",
        "CONFIG": {
            "MODEL_ID": "echo",
            "TOKEN_LIMIT": 123123,
            "MAX_WORD_SLEEP_SECONDS": 0,  # type: ignore
        },
    }
)
def test_prompt_with_context_iterator() -> None:
    backend = get_ai_backend("default")
    response = backend.prompt_with_context(
        pre_prompt="Translate the following context to French.",
        context="I like trains.",
    )
    assert list(response) == [
        "This",
        "is",
        "an",
        "echo",
        "backend:",
        "I",
        "like",
        "trains.",
    ]


def test_get_backend_with_feature(settings) -> None:
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "default": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {"MODEL_ID": "default", "TOKEN_LIMIT": 123123},
            },
            "images": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {"MODEL_ID": "images", "TOKEN_LIMIT": 123123},
            },
        },
        "IMAGE_DESCRIPTION_BACKEND": "images",
    }
    assert get_backend().config.model_id == "default"
    assert get_backend(BackendFeature.TEXT_COMPLETION).config.model_id == "default"
    assert get_backend(BackendFeature.IMAGE_DESCRIPTION).config.model_id == "images"


def test_get_backend_not_found(settings) -> None:
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "default": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {"MODEL_ID": "default", "TOKEN_LIMIT": 123123},
            },
        },
    }
    with pytest.raises(BackendNotFound) as exception:
        get_backend(BackendFeature.IMAGE_DESCRIPTION)
    assert exception.match(r"No backend found for IMAGE_DESCRIPTION")
