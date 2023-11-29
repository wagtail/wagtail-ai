# Installation

At this moment in time the only backend that ships by default with wagtail-ai is [llm](https://llm.datasette.io/en/stable/)
that lets you use a number of different chat models, including OpenAI's.

1. Install the package along with the relevant client libraries for the AI Backend you want to use:
    - For [llm](https://llm.datasette.io/en/stable/) which includes OpenAI chat models,
      `python -m pip install wagtail-ai[llm]`
2. Add `wagtail_ai` to your `INSTALLED_APPS`
3. Add an AI chat model and backend configuration (any model supported by [llm](https://llm.datasette.io/en/stable/)).
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

The openai package can be provided with the API key via the `OPENAI_API_KEY`
environment variable. If you want to provide a custom API key for
each backend please read the llm backend's documentation page.

Read more about the [llm backend here](llm-backend.md).


## Specify the token limit for a backend

!!! info

    Token limit is referred to as "context window" which is the maximum amount
    of tokens in a single context that a specific chat model supports.

If you want to use a chat model that does not have a default token limit configured
or want to change the default token limit, you can do so by adding the `TOKEN_LIMIT`
setting.

```python
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {
            "CLASS": "wagtail_ai.ai.llm.LLMBackend",
            "CONFIG": {
                "MODEL_ID": "gpt-3.5-turbo",
                "TOKEN_LIMIT": 4096,
            },
        }
    }
}
```

This `TOKEN_LIMIT` value depend on the chat model you select as each of them support
a different token limit, e.g. `gpt-3.5-turbo` supports up to 4096 tokens,
`gpt-3.5-turbo-16k` supports up to 16384 tokens.

!!! info "Text splitting"

    [Read more about text splitting and Wagtail AI customization options here](text-splitting.md).
