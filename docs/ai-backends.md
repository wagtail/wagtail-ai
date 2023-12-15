# AI Backends

Wagtail AI can be configured to use different backends to support different AI services.

Currently the only (and default) backend available in Wagtail AI is the [LLM Backend](#llm-backend)

## LLM Backend

This backend uses the [llm library](https://llm.datasette.io/en/stable/) which offers support for many AI services through plugins.

By default, it is configured to use OpenAI's `gpt-3.5-turbo` model.

### Using other models

You can use the command line interface to see the llm models installed in your environment:

```sh
llm models
```

Then you can swap `MODEL_ID` in the configuration to use a different model. For example, to use GPT-4:

```python
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {
            "CLASS": "wagtail_ai.ai.llm.LLMBackend",
            "CONFIG": {
                "MODEL_ID": "gpt-4",
            },
        }
    }
}
```

!!! info

    The `llm` package comes with OpenAI models installed by default.

    You can install other models using [`llm`'s plugin functionality](https://llm.datasette.io/en/stable/plugins/index.html).

### Customisations

There are two settings that you can use with the LLM backend:

- `INIT_KWARGS`
- `PROMPT_KWARGS`

#### `INIT_KWARGS`

These are passed to `llm` as ["Model Options"](https://llm.datasette.io/en/stable/python-api.html#model-options). You can use them to customize the model's initialization.

For example, for OpenAI models you can set a custom API key. By default the `openai` library will use the value of the `OPENAI_API_KEY` environment variable.

```python
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {
            "CLASS": "wagtail_ai.ai.llm.LLMBackend",
            "CONFIG": {
                "MODEL_ID": "gpt-3.5-turbo",  # Model ID recognizable by the llm package.
                "INIT_KWARGS": {"key": "your-custom-api-key"},
            },
        }
    }
}
```

#### `PROMPT_KWARGS`

Using `PROMPT_KWARGS` you can pass arguments to [`llm`'s `prompt` method](https://llm.datasette.io/en/stable/python-api.html#system-prompts), e.g. a system prompt which is passsed with every request.

```python
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {
            "CLASS": "wagtail_ai.ai.llm.LLMBackend",
            "CONFIG": {
                "MODEL_ID": "gpt-3.5-turbo",  # Model ID recognizable by the llm package.
                "PROMPT_KWARGS": {"system": "A custom, global system prompt."},
            },
        }
    }
}
```

#### Specify the token limit for a model

!!! info

    Token limit is referred to as "context window" which is the maximum amount of tokens in a single context that a specific chat model supports.

While Wagtail AI knows the token limit of some models (see [`tokens.py`](https://github.com/wagtail/wagtail-ai/blob/main/src/wagtail_ai/tokens.py)), you might choose to use a model that isn't in this mappping, or you might want to set a lower token limit for an existing model.

You can do this by setting `TOKEN_LIMIT`.

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
