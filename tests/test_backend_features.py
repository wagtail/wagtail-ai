import pytest
from wagtail_ai.ai import get_ai_backend
from wagtail_ai.ai.base import BackendFeature
from wagtail_ai.ai.echo import EchoBackend


@pytest.mark.parametrize(
    "config_features,expected_features",
    [
        (None, {BackendFeature.TEXT_COMPLETION}),
        (["TEXT_COMPLETION"], {BackendFeature.TEXT_COMPLETION}),
        ([], set()),
    ],
)
def test_feature_settings(config_features, expected_features, settings):
    wagtail_ai_settings = {**settings.WAGTAIL_AI}
    backend_settings = {
        "CLASS": "wagtail_ai.ai.echo.EchoBackend",
        "CONFIG": {
            "MODEL_ID": "echo",
            "TOKEN_LIMIT": 123123,
        },
    }
    if config_features is not None:
        backend_settings["CONFIG"]["FEATURES"] = config_features
    wagtail_ai_settings["BACKENDS"]["default"] = backend_settings
    settings.WAGTAIL_AI = wagtail_ai_settings

    backend = get_ai_backend("default")
    assert isinstance(backend, EchoBackend)
    assert backend.config.features == expected_features
