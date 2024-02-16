# Installation

1. Install the package along with the relevant client libraries for the default [AI Backend](ai-backends.md):
   ```bash
   python -m pip install wagtail-ai
   ```
2. Add `wagtail_ai` to your `INSTALLED_APPS`
    ```
    INSTALLED_APPS = [
        # ...
        "wagtail_ai",
    ]
    ```
3. Add an AI chat model and backend configuration (by default, `MODEL_ID` can be any model supported by [the "LLM" library](https://llm.datasette.io/en/stable/)).
    ```python
    WAGTAIL_AI = {
        "BACKENDS": {
            "default": {
                "CLASS": "wagtail_ai.ai.llm.LLMBackend",
                "CONFIG": {
                    # Model ID recognizable by the "LLM" library.
                    "MODEL_ID": "gpt-3.5-turbo",
                },
            }
        }
    }
    ```
4. If you're using an OpenAI model, specify an API key using the `OPENAI_API_KEY` environment variable, or by setting it as a key in [`INIT_KWARGS`](ai-backends.md#init-kwargs).
5. If you've restricted RichText features, add `ai` to your list of features.
    * By default, Wagtail will include all registered features on `RichTextField` and `RichTextBlock` instances. However, [features can be restricted](https://docs.wagtail.org/en/stable/advanced_topics/customisation/page_editing_interface.html#limiting-features-in-a-rich-text-field).
    * If you've restricted features, you must add `ai` to the list of features for the Wagtail AI button to appear on RichText fields/blocks.
