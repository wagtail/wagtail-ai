# AI Providers

Wagtail AI uses [django-ai-core](https://github.com/wagtail/django-ai-core) and the [any-llm](https://github.com/mozilla-ai/any-llm) library to support multiple AI providers and models. This unified interface allows integrations with OpenAI, Anthropic Claude, local models, and many other AI services.

!!! note

    Providers will replace the previous concept of [AI Backends](./ai-backends.md) introduced in Wagtail AI 2.x. If you're upgrading from Wagtail AI 2.x, see the [migration instructions](./upgrading.md).

## Quick start

Configure AI providers in your Django settings using the `WAGTAIL_AI` configuration:

```python
WAGTAIL_AI = {
    "PROVIDERS": {
        "default": {
            "provider": "openai",
            "model": "gpt-4.1-mini",
        },
    },
}
```

## Multiple providers

The `any-llm` library supports [a wide range of providers](https://mozilla-ai.github.io/any-llm/providers/). Apart from `model`, the dictionary of a provider is passed as keyword arguments to `any-llm`'s [`AnyLLM.create()`](https://mozilla-ai.github.io/any-llm/api/any_llm/#any_llm.AnyLLM.create).

For example, the following configuration has two different providers: a `default` provider for general text tasks, and a `vision` provider for image-related features using a vision-capable model. Both providers are hosted by different services by passing custom `api_key` and `api_base` values.

```python
WAGTAIL_AI = {
    "PROVIDERS": {
        "default": {
            "provider": "openai",
            "model": "gpt-oss-120b",
            "api_key": "my-scaleway-key",
            "api_base": "https://api.scaleway.ai/my-project-id/v1",
        },
        "vision": {
            "provider": "mistral",
            "model": "mistral-small-3.2-24b-instruct-2506",
            "api_key": "my-own-secret-key",
            "api_base": "https://my-llm-host.com/v1",
        },
    },
    "IMAGE_DESCRIPTION_PROVIDER": "vision",  # Use vision model for images
}
```

!!! note

    You may have to install additional dependencies for some providers. See the [any-llm documentation](https://mozilla-ai.github.io/any-llm/providers/) and the individual provider documentation for details.
