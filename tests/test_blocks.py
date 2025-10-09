import json
from unittest.mock import patch

from wagtail.blocks import CharBlock, StructBlock
from wagtail.images.blocks import ImageBlock, ImageChooserBlock

from wagtail_ai.agents.basic_prompt import ContextualAltTextPrompt
from wagtail_ai.blocks import (
    AIImageBlock,
    AIImageBlockAdapter,
    ai_image_block,
    get_image_block_form_attrs,
)


class TestGetImageBlockFormAttrs:
    def test_default_parameters(self):
        attrs = get_image_block_form_attrs()

        assert attrs["data-controller"] == "wai-field-panel"
        assert (
            attrs["data-wai-field-panel-main-input-value"]
            == '[data-contentpath="alt_text"] input'
        )
        assert (
            attrs["data-wai-field-panel-image-input-value"]
            == '[data-contentpath="image"] input'
        )
        assert attrs["data-wai-field-panel-prompts-value"] == json.dumps(
            [ContextualAltTextPrompt.name]
        )

    def test_custom_field_names(self):
        attrs = get_image_block_form_attrs(
            alt_text_field_name="custom_alt",
            image_field_name="custom_image",
        )

        assert attrs["data-controller"] == "wai-field-panel"
        assert (
            attrs["data-wai-field-panel-main-input-value"]
            == '[data-contentpath="custom_alt"] input'
        )
        assert (
            attrs["data-wai-field-panel-image-input-value"]
            == '[data-contentpath="custom_image"] input'
        )
        assert attrs["data-wai-field-panel-prompts-value"] == json.dumps(
            [ContextualAltTextPrompt.name]
        )


class TestAIImageBlock:
    def test_inherits_from_image_block(self):
        block = AIImageBlock()
        assert isinstance(block, AIImageBlock)
        assert isinstance(block, ImageBlock)

    def test_form_attrs_configuration(self):
        block = AIImageBlock()
        form_attrs = block.meta.form_attrs

        assert form_attrs["data-controller"] == "wai-field-panel"
        assert (
            form_attrs["data-wai-field-panel-main-input-value"]
            == '[data-contentpath="alt_text"] input'
        )
        assert (
            form_attrs["data-wai-field-panel-image-input-value"]
            == '[data-contentpath="image"] input'
        )
        assert form_attrs["data-wai-field-panel-prompts-value"] == json.dumps(
            [ContextualAltTextPrompt.name]
        )

    def test_uses_default_form_attrs(self):
        expected_attrs = get_image_block_form_attrs()
        block = AIImageBlock()
        actual_attrs = block.meta.form_attrs

        assert expected_attrs == actual_attrs


class TestAIImageBlockDecorator:
    def test_custom_struct_block_with_decorator(self):
        with patch("wagtail_ai.blocks.register") as mock_register:

            @ai_image_block(
                alt_text_field_name="caption",
                image_field_name="photo",
                prompts=["custom_prompt"],
            )
            class CustomImageBlock(StructBlock):
                photo = ImageChooserBlock()
                caption = CharBlock()

        assert mock_register.call_count == 1

        call_args = mock_register.call_args[0]
        adapter = call_args[0]
        block_class = call_args[1]

        assert isinstance(adapter, AIImageBlockAdapter)
        assert block_class is CustomImageBlock

        block = CustomImageBlock()
        expected_form_attrs = get_image_block_form_attrs(
            alt_text_field_name="caption",
            image_field_name="photo",
            prompts=["custom_prompt"],
        )
        assert block.meta.form_attrs == expected_form_attrs

        assert block.meta.form_attrs["data-controller"] == "wai-field-panel"
        assert (
            block.meta.form_attrs["data-wai-field-panel-main-input-value"]
            == '[data-contentpath="caption"] input'
        )
        assert (
            block.meta.form_attrs["data-wai-field-panel-image-input-value"]
            == '[data-contentpath="photo"] input'
        )
        assert block.meta.form_attrs[
            "data-wai-field-panel-prompts-value"
        ] == json.dumps(["custom_prompt"])
