from functools import wraps
from typing import Any, Literal, cast

from django.conf import settings
from django.test import override_settings
from wagtail_ai.ai import AIBackendSettingsDict


def custom_wagtail_ai_backend_settings(
    *, settings_key: Literal["CLASS", "CONFIG", "TEXT_SPLITTING"], new_value: Any
):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            value = {**settings.WAGTAIL_AI}
            default_backend = cast(
                AIBackendSettingsDict,
                {
                    **settings.WAGTAIL_AI["BACKENDS"]["default"],
                },
            )
            default_backend[settings_key] = new_value
            value["BACKENDS"]["default"] = default_backend
            return override_settings(WAGTAIL_AI=value)(func)(*args, **kwargs)

        return inner

    return decorator
