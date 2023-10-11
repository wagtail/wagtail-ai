# Installation

1. Install the package along with the relevant client libraries for the AI Backend you want to use:
    - For OpenAI, `python -m pip install wagtail-ai[openai]`
    - For Anthropic, `python -m pip install wagtail-ai[anthropic]`
2. Add `wagtail_ai` to your `INSTALLED_APPS`
3. Add an AI backend configuration (any backend supported by [https://github.com/tomusher/every-ai](EveryAI)):
    ```python
    WAGTAIL_AI_BACKENDS = {
        "default": {"BACKEND": "openai", "CONFIG": {"api_key": "api_key"}}
    }
    ```
