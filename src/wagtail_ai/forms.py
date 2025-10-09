import json
from functools import cached_property

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.admin.staticfiles import versioned_static
from wagtail.images.forms import BaseImageForm

from wagtail_ai.agents.basic_prompt import ImageDescriptionPrompt, ImageTitlePrompt
from wagtail_ai.models import Prompt


class PromptTextField(forms.CharField):
    default_error_messages = {
        "required": _(
            "No text provided - please enter some text before using AI features."
        ),
    }


class PromptUUIDField(forms.UUIDField):
    default_error_messages = {
        "required": _("Invalid prompt provided."),
        "invalid": _("Invalid prompt provided."),
    }


class ApiForm(forms.Form):
    def errors_for_json_response(self) -> str:
        errors_for_response = []
        for _field, errors in self.errors.get_json_data().items():
            for error in errors:
                errors_for_response.append(error["message"])

        return " \n".join(errors_for_response)


class PromptForm(ApiForm):
    text = PromptTextField()
    prompt = PromptUUIDField()

    def clean_prompt(self):
        prompt_uuid = self.cleaned_data["prompt"]
        prompt = Prompt.objects.filter(uuid=prompt_uuid).first()
        if not prompt:
            raise ValidationError(
                self.fields["prompt"].error_messages["invalid"], code="invalid"
            )

        return prompt


class DescribeImageApiForm(ApiForm):
    image_id = forms.CharField()
    maxlength = forms.IntegerField(required=False, min_value=0, max_value=4096)


class ImageDescriptionWidgetMixin(forms.Widget):
    """
    A widget mixin that wraps the widget in a controller for describing images.
    Can be used with TextInput or Textarea.
    """

    def __init__(
        self,
        *args,
        image_id=None,
        file_selector=None,
        prompts=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.attrs["data-controller"] = " ".join(
            {
                *self.attrs.get("data-controller", "").split(),
                "wai-field-panel",
            }
        )
        if image_id:
            self.attrs["data-wai-field-panel-image-id"] = image_id
        self.attrs["data-wai-field-panel-image-input-value"] = file_selector
        self.attrs["data-wai-field-panel-prompts-value"] = json.dumps(
            prompts or [ImageDescriptionPrompt.name]
        )

    @cached_property
    def media(self):  # type: ignore
        return forms.Media(
            js=[
                versioned_static("wagtail_ai/field_panel.js"),
            ],
            css={
                "all": [versioned_static("wagtail_ai/field_panel.css")],
            },
        )


class ImageDescriptionTextInput(ImageDescriptionWidgetMixin, forms.TextInput):
    pass


class DescribeImageForm(BaseImageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widget_kwargs = {}
        if "file" in self.fields:
            widget_kwargs["file_selector"] = f"#{self['file'].id_for_label}"
        if self.instance and self.instance.pk:
            widget_kwargs["image_id"] = self.instance.pk

        self.fields["title"].widget = ImageDescriptionTextInput(
            **widget_kwargs,
            prompts=[ImageTitlePrompt.name],
            attrs=self.fields["title"].widget.attrs,
        )
        self.fields["description"].widget = ImageDescriptionTextInput(
            **widget_kwargs,
            prompts=[ImageDescriptionPrompt.name],
            attrs=self.fields["description"].widget.attrs,
        )
