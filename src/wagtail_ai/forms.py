from functools import cached_property

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from wagtail.admin.staticfiles import versioned_static
from wagtail.images.fields import WagtailImageField
from wagtail.images.forms import BaseImageForm


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
        if prompt_uuid.version != 4:
            raise ValidationError(
                self.fields["prompt"].error_messages["invalid"], code="invalid"
            )

        return prompt_uuid


class DescribeImageApiForm(ApiForm):
    image_id = forms.CharField(required=False)
    file = WagtailImageField(required=False)
    maxlength = forms.IntegerField(required=False, min_value=0, max_value=4096)

    def clean(self):
        cleaned_data = super().clean()
        image_id = cleaned_data.get("image_id")
        file = cleaned_data.get("file")

        if not image_id and not file:
            raise ValidationError(gettext("Please provide an image."), code="invalid")

        return cleaned_data


class ImageDescriptionWidget(forms.TextInput):
    template_name = "wagtail_ai/widgets/image_description.html"

    def __init__(self, *args, image_id=None, file_selector=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs["data-wai-describe-target"] = "input"
        self.image_id = image_id
        self.file_selector = file_selector

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["image_id"] = self.image_id
        context["file_selector"] = self.file_selector
        return context


class DescribeImageForm(BaseImageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widget_kwargs = {"file_selector": f"#{self['file'].id_for_label}"}
        if self.instance and self.instance.pk:
            widget_kwargs["image_id"] = self.instance.pk

        self.fields["title"].widget = ImageDescriptionWidget(**widget_kwargs)

    @cached_property
    def media(self):  # type: ignore
        return super().media + forms.Media(
            js=[
                versioned_static("wagtail_ai/image_description.js"),
            ],
            css={
                "all": [versioned_static("wagtail_ai/image_description.css")],
            },
        )
