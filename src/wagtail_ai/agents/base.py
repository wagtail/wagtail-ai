from functools import cache

from django_ai_core.llm import LLMService

from wagtail_ai import ai


@cache
def get_llm_service(provider="openai"):
    # TODO: deprecate the backends and have a proper setting for configuring
    # the provider and model
    backend = ai.get_backend()
    return LLMService.create(provider=provider, model=backend.config.model_id)
