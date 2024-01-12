from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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


class PromptForm(forms.Form):
    text = PromptTextField()
    prompt = PromptUUIDField()

    def clean_prompt(self):
        prompt_uuid = self.cleaned_data["prompt"]
        if prompt_uuid.version != 4:
            raise ValidationError(
                self.fields["prompt"].error_messages["invalid"], code="invalid"
            )

        return prompt_uuid

    def errors_for_json_response(self) -> str:
        errors_for_response = []
        for _field, errors in self.errors.get_json_data().items():
            for error in errors:
                errors_for_response.append(error["message"])

        return " \n".join(errors_for_response)
