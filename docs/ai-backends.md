# AI Backends

Wagtail AI can be configured to use different backends to support different AI services.

Currently the only (and default) backend available in Wagtail AI is the ["LLM" backend](#the-llm-backend).

## The "LLM" backend

This backend uses the ["LLM" library](https://llm.datasette.io/en/stable/) which offers support for many AI services through plugins.

By default, it is configured to use OpenAI's `gpt-3.5-turbo` model.

### Using other models

You can use the command line interface to see the "LLM" library's models installed in your environment:

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

    The "LLM" library comes with OpenAI models installed by default.

    You can install other models using [the "LLM" library's plugin functionality](https://llm.datasette.io/en/stable/plugins/index.html).

### Customisations

There are two settings that you can use with the "LLM" backend:

- `INIT_KWARGS`
- `PROMPT_KWARGS`

#### `INIT_KWARGS`

These are passed to the "LLM" library as ["Model Options"](https://llm.datasette.io/en/stable/python-api.html#model-options).
You can use them to customize the model's initialization.

For example, for OpenAI models you can set a custom API key. By default the OpenAI Python library
will use the value of the `OPENAI_API_KEY` environment variable.

```python
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {
            "CLASS": "wagtail_ai.ai.llm.LLMBackend",
            "CONFIG": {
                # Model ID recognizable by the llm library.
                "MODEL_ID": "gpt-3.5-turbo",
                "INIT_KWARGS": {"key": "your-custom-api-key"},
            },
        }
    }
}
```

#### `PROMPT_KWARGS`

Using `PROMPT_KWARGS` you can pass arguments to [the "LLM" library's `prompt` method](https://llm.datasette.io/en/stable/python-api.html#system-prompts),
e.g. a system prompt which is passed with every request.

```python
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {
            "CLASS": "wagtail_ai.ai.llm.LLMBackend",
            "CONFIG": {
                # Model ID recognizable by the "LLM" library.
                "MODEL_ID": "gpt-3.5-turbo",
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

#### Using a custom OpenAI or OpenAI-compatible model

The "LLM" library supports adding custom OpenAI models. This may be necessary if:

- You want to use a model that's not supported by the "LLM" library yet.
- You want to use a proxy for OpenAI requests.

You can find the "LLM" library specific instructions at: https://llm.datasette.io/en/stable/other-models.html#adding-more-openai-models.

1. Find the "LLM" library's directory. You can set a custom one with the. You can
   set a custom one with the
   [`LLM_USER_PATH`](https://llm.datasette.io/en/stable/setup.html#setting-a-custom-directory-location)
   setting. You can then confirm the path with the following shell command:
   `dirname "$(llm logs path)"`.
2. Create `extra-openai-models.yaml` as noted in
   [the "LLM" library's documentation](https://llm.datasette.io/en/stable/other-models.html#adding-more-openai-models).
   For example to set up a proxy:
   ```yaml
    - model_id: customgateway-gpt-3.5-turbo
      model_name: gpt-3.5-turbo
      api_base: "https://yourcustomproxy.example.com/"
      headers:
        apikey: your-api-key
   ```
3. Set the `MODEL_ID` in the Wagtail AI settings in your Django project
   settings to the `model_id` you set in the yaml file.
   ```python
   WAGTAIL_AI = {
       "BACKENDS": {
           "default": {
               "CLASS": "wagtail_ai.ai.llm.LLMBackend",
               "CONFIG": {
                   # MODEL_ID should match the model_id in the yaml file.
                   "MODEL_ID": "customgateway-gpt-3.5-turbo",
                   # TOKEN_LIMIT has to be defined because you use a custom model name.
                   # You are looking to use the context window value from:
                   # https://platform.openai.com/docs/models/gpt-3-5
                   "TOKEN_LIMIT": 4096,
               },
           }
       }
   }
   ```
