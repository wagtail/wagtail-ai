# llm backend

wagtail-ai comes with a backend for the [llm library](https://llm.datasette.io/en/stable/)
out-of-the box.

## Using other "llm" models

You can use the command line interface to see the llm models installed in your environment:

```sh
llm models
```

Then you can swap `MODEL_ID` in the configuration to use a different model.

!!! info

    At this moment in time, the llm package comes with OpenAI models installed by default.

    You can install other models via the [llm's plugins functionality](https://llm.datasette.io/en/stable/plugins/index.html).

## "llm" backend custom settings

There are two custom settings that you can use with the llm backend:

- `INIT_KWARGS`
- `PROMPT_KWARGS`

### `INIT_KWARGS`

Those are set on the model instance. You can use them to customize the model's initialization.

See more details about the available options on https://llm.datasette.io/en/stable/python-api.html#model-options.

#### Custom OpenAI key

E.g. for OpenAI models you can set a custom API key. Otherwise the `openai` library will use whatever
you've set up in your environment with `OPENAI_API_KEY`.

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

### `PROMPT_KWARGS`

You can pass arguments to the [llm's `prompt` method](https://llm.datasette.io/en/stable/python-api.html#system-prompts).

E.g. a system prompt.

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
