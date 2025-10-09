import json

from django import forms
from django.utils.functional import cached_property
from wagtail.admin.staticfiles import versioned_static
from wagtail.admin.telepath import register
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.images.blocks import ImageBlock

from wagtail_ai.agents.basic_prompt import ContextualAltTextPrompt


def get_image_block_form_attrs(
    alt_text_field_name: str = "alt_text",
    image_field_name: str = "image",
    prompts=None,
):
    prompts = prompts or [ContextualAltTextPrompt.name]
    return {
        "data-controller": "wai-field-panel",
        "data-wai-field-panel-main-input-value": f'[data-contentpath="{alt_text_field_name}"] input',
        "data-wai-field-panel-image-input-value": f'[data-contentpath="{image_field_name}"] input',
        "data-wai-field-panel-prompts-value": json.dumps(prompts),
    }


class AIImageBlockAdapter(StructBlockAdapter):
    js_constructor = "wagtail_ai.blocks.AIImageBlock"

    @cached_property
    def media(self):
        return super().media + forms.Media(
            js=[
                versioned_static("wagtail_ai/field_panel.js"),
                versioned_static("wagtail_ai/image_block.js"),
            ],
            css={"all": [versioned_static("wagtail_ai/field_panel.css")]},
        )


def ai_image_block(
    alt_text_field_name: str = "alt_text",
    image_field_name: str = "image",
    prompts=None,
):
    """Decorator for a block class to set the appropriate form attributes for AI image features."""

    def decorator(block_class):
        block_class._meta_class.form_attrs = {
            **(block_class._meta_class.form_attrs or {}),
            **get_image_block_form_attrs(
                alt_text_field_name=alt_text_field_name,
                image_field_name=image_field_name,
                prompts=prompts,
            ),
        }
        register(AIImageBlockAdapter(), block_class)
        return block_class

    return decorator


@ai_image_block()
class AIImageBlock(ImageBlock):
    pass
