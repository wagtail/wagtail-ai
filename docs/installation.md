# Installation

1. Install the package along with the relevant client libraries for the default [AI Backend](ai-backends.md):
   ```bash
   python -m pip install wagtail-ai[llm]
   ```
2. Add `wagtail_ai` to your `INSTALLED_APPS`
    ```
    INSTALLED_APPS = [
        "wagtail_ai",
        # ...
    ]
    ```
3. Add an AI chat model and backend configuration (by default, `MODEL_ID` can be any model supported by [llm](https://llm.datasette.io/en/stable/)).
    ```python
    WAGTAIL_AI = {
        "BACKENDS": {
            "default": {
                "CLASS": "wagtail_ai.ai.llm.LLMBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-3.5-turbo",  # Model ID recognizable by the llm package.
                },
            }
        }
    }
    ```
4. If you're using an OpenAI model, specify an API key using the `OPENAI_API_KEY` environment variable, or by setting it as a key in [`INIT_KWARGS`](ai-backends.md#init-kwargs).
