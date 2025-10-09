# Upgrading Wagtail AI

## Changes in 3.0

### Dropped support for Wagtail < 7.1

Wagtail AI now requires Wagtail 7.1+ to be installed.

### `PROVIDERS` must be configured

You must add a `PROVIDERS` setting to your `WAGTAIL_AI` configuration.

```py
WAGTAIL_AI = {
    "PROVIDERS": {
        "default": {
            "provider": "openai",
            "model": "gpt-4.1-mini",
        },
    },
    # ...
}
```

If not configured, Wagtail AI will try to create a default provider using the `MODEL_ID` from the `default` backend, with `provider` set to `openai`. However, this fallback behaviour is deprecated and will be removed in a future release.

See [AI Providers](./ai-providers.md) for more details.

### `IMAGE_DESCRIPTION_BACKEND` replaced with `IMAGE_DESCRIPTION_PROVIDER`

The `IMAGE_DESCRIPTION_BACKEND` setting has been replaced with `IMAGE_DESCRIPTION_PROVIDER`. This setting now refers to a provider configured in the `PROVIDERS` setting instead of a backend.
