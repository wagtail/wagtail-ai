# Images integration

Wagtail AI integrates with image upload and edit forms to provide AI-generated titles and descriptions. The integration requires a model that supports vision.

## Configuring the AI provider

Set up an AI provider that supports vision/image understanding in your Django settings:

```python
WAGTAIL_AI = {
    "PROVIDERS": {
        "default": {
            "provider": "openai",
            "model": "gpt-oss-120b",
        },
        "vision": {
            "provider": "mistral",
            "model": "mistral-small-3.2-24b-instruct-2506",
        },
    },
    "IMAGE_DESCRIPTION_PROVIDER": "vision",  # Use vision model for images
}
```

If your `default` provider is vision-capable, you can omit the `vision` provider and `IMAGE_DESCRIPTION_PROVIDER` setting.

## Title and description generation

Configure Wagtail to use the AI-enhanced image form:

```python
WAGTAILIMAGES_IMAGE_FORM_BASE = "wagtail_ai.forms.DescribeImageForm"
```

Now when you upload or edit an image, magic wand icons will appear next to both the **title** and **description** fields.

For the title field, you get the option to generate a concise, descriptive title for your image based on its visual content. For the description field, you get the option to generate a detailed description suitable for alt text and image metadata.

The prompts for both features can be customized in **Settings -> Agent** in the Wagtail admin under "Image title prompt" and "Image description prompt". These prompts allow the following placeholder tokens to be used:

- `{image}`: The image to describe (required)
- `{max_length}`: The maximum length (in characters) set on the input widget

### Custom form

Wagtail AI includes an image form that enhances the `title` field with an AI button. If you are using a [custom image model](https://docs.wagtail.org/en/stable/advanced_topics/images/custom_image_model.html), you can provide your own form to target another field. Check out the implementation of `DescribeImageForm` in [`forms.py`](https://github.com/wagtail/wagtail-ai/blob/main/src/wagtail_ai/forms.py), adapt it to your needs, and set it as `WAGTAILIMAGES_IMAGE_FORM_BASE`.

## Contextual image alt text

Wagtail AI can generate contextual alt text for images based on both the image content and the surrounding page content. This creates more meaningful, accessible alt text that considers the context in which the image appears. This is made possible by using the `AIImageBlock` in `StreamField`s.

### `AIImageBlock`

The `AIImageBlock` is a drop-in replacement for Wagtail's standard [`ImageBlock`](https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html#wagtail.images.blocks.ImageBlock) that adds AI-powered contextual alt text generation.

**Usage in StreamField:**

```python
from wagtail import blocks
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail_ai.blocks import AIImageBlock


class BlogPage(Page):
    body = StreamField(
        [
            ("paragraph", blocks.RichTextBlock()),
            ("image", AIImageBlock()),
            # Other block types...
        ]
    )
```

When an editor selects an image in the `AIImageBlock`, they'll see a magic wand icon next to the alt text field. Clicking it generates alt text that considers:

- The image itself
- The content before the image in the page
- The content after the image in the page

This contextual awareness helps create more relevant alt text than image-only analysis.

### Custom image blocks with @ai_image_block

For custom image blocks with different field names, use the `@ai_image_block` decorator:

```python
from wagtail import blocks
from wagtail_ai.blocks import ai_image_block


@ai_image_block(
    alt_text_field_name="caption",
    image_field_name="photo",
)
class CustomImageBlock(blocks.StructBlock):
    photo = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)
```

**Decorator parameters:**

- `alt_text_field_name` (default: `'alt_text'`): The name of the alt text field in your block
- `image_field_name` (default: `'image'`): The name of the image field in your block

### Configuring the prompt

The default contextual alt text prompt can be customized in **Settings → Agent** in the Wagtail admin under "Images > Contextual alt text prompt".

The following placeholder tokens are available to use in the prompt:

- `{image}`: The image to describe
- `{form_context_before}`: Text content in the page editor before the image
- `{form_context_after}`: Text content in the page editor after the image
- `{max_length}`: The maximum length (in characters) set on the alt text input widget
- `{input}`: The current value of the alt text input widget

## Configuring image rendition

For optimal performance and cost, Wagtail AI resizes images before sending them to the AI provider. Configure the rendition filter:

```python
WAGTAIL_AI = {
    "PROVIDERS": {
        # ...
    },
    "IMAGE_DESCRIPTION_RENDITION_FILTER": "max-800x600",  # Default
}
```

This helps control API costs while maintaining sufficient image quality for AI analysis.

The setting is currently only used for images that have already been uploaded to Wagtail. During new uploads, Wagtail AI will use the original image.
