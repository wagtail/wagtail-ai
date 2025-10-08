import json

from wagtail.images.blocks import ImageBlock

from wagtail_ai.agents.basic_prompt import ContextualAltTextPrompt
from wagtail_ai.blocks import AIImageBlock, get_image_block_form_attrs


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
