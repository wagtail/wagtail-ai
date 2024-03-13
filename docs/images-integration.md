# Images Integration

Wagtail AI integrates with the image edit form to provide AI-generated descriptions to images. The integration requires a backend that supports image descriptions, such as [the OpenAI backend](../ai-backends/#the-openai-backend).

## Configuration

1. In the Django project settings, configure an AI backend, and a model, that support images. Set `IMAGE_DESCRIPTION_BACKEND` to the name of the backend:
   ```python
   WAGTAIL_AI = {
       "BACKENDS": {
           "vision": {
               "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
               "CONFIG": {
                   "MODEL_ID": "gpt-4-vision-preview",
                   "TOKEN_LIMIT": 300,
               },
           },
       },
       "IMAGE_DESCRIPTION_BACKEND": "vision",
   }
   ```
2. In the Django project settings, configure a [custom Wagtail image base form](https://docs.wagtail.org/en/stable/reference/settings.html#wagtailimages-image-form-base):
   ```python
   WAGTAILIMAGES_IMAGE_FORM_BASE = "wagtail_ai.forms.DescribeImageForm"
   ```

Now, when you upload or edit an image, a magic wand icon should appear next to the _title_ field. Clicking on the icon will invoke the AI backend to generate an image description.

## Separate backends for text completion and image description

Multi-modal models are faily new, so you may want to configure two different backends for text completion and image description. The `default` model will be used for text completion:

```python
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {
            "CLASS": "wagtail_ai.ai.llm.LLMBackend",
            "CONFIG": {
                "MODEL_ID": "gpt-3.5-turbo",
            },
        },
        "vision": {
            "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
            "CONFIG": {
                "MODEL_ID": "gpt-4-vision-preview",
                "TOKEN_LIMIT": 300,
            },
        },
    },
    "IMAGE_DESCRIPTION_BACKEND": "vision",
}
```

## Custom prompt

Wagtail AI includes a simple prompt to ask the AI to generate an image description:

> Describe this image. Make the description suitable for use as an alt-text.

If you want to use a different prompt, override the `IMAGE_DESCRIPTION_PROMPT` value:

```python
WAGTAIL_AI = {
    "BACKENDS": {
        # ...
    },
    "IMAGE_DESCRIPTION_PROMPT": "Describe this image in the voice of Sir David Attenborough.",
}
```

## Custom form

Wagtail AI includes an image form that enhances the `title` field with an AI button. If you are using a [custom image model](https://docs.wagtail.org/en/stable/advanced_topics/images/custom_image_model.html), you can provide your own form to target another field. Check out the implementation of `DescribeImageForm` in [`forms.py`](https://github.com/wagtail/wagtail-ai/blob/main/src/wagtail_ai/forms.py), adapt it to your needs, and set it as `WAGTAILIMAGES_IMAGE_FORM_BASE`.
