from functools import cache
from typing import TYPE_CHECKING, cast

from django.conf import settings
from django.utils.module_loading import import_string
from django_ai_core.llm import LLMService
from wagtail.contrib.settings.models import BaseGenericSetting, BaseSiteSetting
from wagtail.models import Site

from wagtail_ai import ai

if TYPE_CHECKING:
    from wagtail_ai.models import AgentSettingsMixin


@cache
def get_llm_service(provider="openai"):
    # TODO: deprecate the backends and have a proper setting for configuring
    # the provider and model
    backend = ai.get_backend()
    return LLMService.create(provider=provider, model=backend.config.model_id)


def get_agent_settings_model() -> "type[BaseGenericSetting | BaseSiteSetting]":
    wagtail_ai_settings = getattr(settings, "WAGTAIL_AI", {})
    model_path = wagtail_ai_settings.get(
        "AGENT_SETTINGS_MODEL",
        "wagtail_ai.models.AgentSettings",
    )
    return import_string(model_path)


def get_agent_settings() -> "AgentSettingsMixin":
    model = get_agent_settings_model()
    if issubclass(model, BaseSiteSetting):
        # TODO: support multiple sites
        settings = model.for_site(site=Site.objects.first())
    else:
        settings = model.load()

    return cast("AgentSettingsMixin", settings)
