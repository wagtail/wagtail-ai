from wagtail.images.blocks import ImageBlock

from wagtail_ai.prompts import DefaultPrompt


def get_image_block_form_attrs(
    alt_text_field_name: str = "alt_text",
    image_field_name: str = "image",
):
    return {
        "data-controller": "wai-field-panel",
        "data-wai-field-panel-main-input-value": f'[data-contentpath="{alt_text_field_name}"] input',
        "data-wai-field-panel-image-input-value": f'[data-contentpath="{image_field_name}"] input',
        "data-wai-field-panel-prompts-value": f"[{DefaultPrompt.CONTEXTUAL_ALT_TEXT}]",
    }


class AIImageBlock(ImageBlock):
    class Meta:  # type: ignore
        form_attrs = get_image_block_form_attrs()
