from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.admin.staticfiles import versioned_static
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
    image_id = forms.CharField()
    maxlength = forms.IntegerField(required=False, min_value=0, max_value=4096)


class DescribeImageForm(BaseImageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            widget = self.fields["title"].widget
            widget.attrs["data-wagtailai-image-id"] = str(self.instance.pk)
            widget.attrs["data-wagtailai-button-title"] = _("Describe image using AI")
            widget.template_name = "wagtail_ai/widgets/image_title.html"

    class Media:
        js = [versioned_static("wagtail_ai/image_description.js")]
        css = {"all": [versioned_static("wagtail_ai/image_description.css")]}
