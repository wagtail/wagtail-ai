# Installation

1. `python -m pip install wagtail-ai`
2. Add `wagtail_ai` to your `INSTALLED_APPS`
3. Add an AI backend configuration (currently only OpenAI is supported):
    ```python
    WAGTAIL_AI_BACKENDS = {
        "default": {
            "BACKEND": "wagtail_ai.ai_backends.openai.OpenAIBackend",
            "API_KEY": "openai_api_key",
        }
    }
    ```
4. Set up a [vector backend](./vector-search/backends.md) if necessary
