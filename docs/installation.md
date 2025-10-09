# Installation

## Requirements

- Python 3.11+
- Django 4.2+
- Wagtail 7.1+

## Quick start

1. Install Wagtail AI:
   ```bash
   python -m pip install wagtail-ai
   ```

2. Add to INSTALLED_APPS:
   ```python
   INSTALLED_APPS = [
       # ...
       "wagtail_ai",
       # Ensure wagtail_ai is listed before Wagtail apps
       # ...
   ]
   ```

3. Configure an AI Provider and Backend:

    ```python
    WAGTAIL_AI = {
        "PROVIDERS": {
            "default": {
                "provider": "openai",
                "model": "gpt-4.1-mini",
            },
        },
        # For legacy rich text editor integration
        "BACKENDS": {
            "default": {
                "CLASS": "wagtail_ai.ai.llm.LLMBackend",
                "CONFIG": {
                    # Model ID recognizable by the "LLM" library.
                    "MODEL_ID": "gpt-3.5-turbo",
                },
            }
        },
    }
    ```

4. If you're using an OpenAI model, specify an API key using the `OPENAI_API_KEY` environment variable, or pass it in a provider setting as `api_key`. Refer to the [AI Providers](./ai-providers.md) and [AI Backends](./ai-backends.md) documentation for more details.

5. Run migrations:

    ```bash
    python manage.py migrate
    ```

6. Enable specific features:

    - [Rich text editor integration](./editor-integration.md)
    - [Field panel integration](./field-panel-integration.md)
    - [Image features](./images-integration.md)
    - [Contextual alt text](./contextual-alt-text.md)
    - [Content feedback](./content-feedback.md)
    - [Related pages](./related-pages.md)
