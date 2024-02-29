from wagtail_ai.ai import get_ai_backend, get_ai_backend_with_feature
from wagtail_ai.ai.base import BackendFeature


def test_feature_settings(settings):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "default": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo default",
                    "TOKEN_LIMIT": 123123,
                },
            },
            "strings": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo strings",
                    "TOKEN_LIMIT": 123123,
                    "FEATURES": ["IMAGE_DESCRIPTION"],
                },
            },
            "enums": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo enums",
                    "TOKEN_LIMIT": 123123,
                    "FEATURES": [BackendFeature.IMAGE_DESCRIPTION],
                },
            },
            "empty": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo empty",
                    "TOKEN_LIMIT": 123123,
                    "FEATURES": [],
                },
            },
        },
    }

    assert get_ai_backend("default").config.features == {BackendFeature.TEXT_COMPLETION}
    assert get_ai_backend("strings").config.features == {
        BackendFeature.IMAGE_DESCRIPTION
    }
    assert get_ai_backend("enums").config.features == {BackendFeature.IMAGE_DESCRIPTION}
    assert get_ai_backend("empty").config.features == set()


def test_get_backend_with_feature_returns_first_match(settings):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "default": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo default",
                    "TOKEN_LIMIT": 123123,
                    "FEATURES": [],
                },
            },
            "first": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo first",
                    "TOKEN_LIMIT": 123123,
                    "FEATURES": ["TEXT_COMPLETION"],
                },
            },
            "second": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo second",
                    "TOKEN_LIMIT": 123123,
                    "FEATURES": ["TEXT_COMPLETION"],
                },
            },
        },
    }

    text_backend = get_ai_backend_with_feature(BackendFeature.TEXT_COMPLETION)
    assert text_backend is not None
    assert text_backend.config.model_id == "echo first"

    assert get_ai_backend_with_feature(BackendFeature.IMAGE_DESCRIPTION) is None
