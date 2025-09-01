from functools import wraps
from typing import Any, Literal, cast

from django.conf import settings
from django.test import override_settings

from wagtail_ai.ai import AIBackendSettingsDict, TextSplittingSettingsDict

DEFAULT_ALIAS = "default"


def custom_ai_backend_settings(
    *, alias: str = DEFAULT_ALIAS, new_value: AIBackendSettingsDict
):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            value = {**settings.WAGTAIL_AI}
            value["BACKENDS"][alias] = new_value
            return override_settings(WAGTAIL_AI=value)(func)(*args, **kwargs)

        return inner

    return decorator


def custom_ai_backend_specific_settings(
    *,
    settings_key: Literal["CLASS", "CONFIG", "TEXT_SPLITTING"],
    new_value: Any,
    alias: str = DEFAULT_ALIAS,
):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            backend_settings = cast(
                AIBackendSettingsDict,
                {
                    **settings.WAGTAIL_AI["BACKENDS"][alias],
                },
            )
            backend_settings[settings_key] = new_value
            return custom_ai_backend_settings(new_value=backend_settings, alias=alias)(
                func
            )(*args, **kwargs)

        return inner

    return decorator


def custom_text_splitting(new_settings: TextSplittingSettingsDict):
    return custom_ai_backend_specific_settings(
        settings_key="TEXT_SPLITTING", new_value=new_settings, alias="default"
    )


def custom_ai_backend_class(new_path: str):
    return custom_ai_backend_specific_settings(settings_key="CLASS", new_value=new_path)
