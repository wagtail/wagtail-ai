import logging
import os

from django import forms
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.admin.viewsets.model import ModelViewSet

from . import ai, types
from .forms import PromptForm
from .models import Prompt

logger = logging.getLogger(__name__)


class AIHandlerException(Exception):
    pass


def _process_backend_request(
    ai_backend: ai.AIBackend, pre_prompt: str, context: str
) -> types.AIResponse:
    """
    Method for processing prompt requests and handling errors.

    Errors will either be an API or Python library error, this method uses exception
    chaining to retain the original error and raise a more generic error message to be sent to the front-end.

    :return: The response message from the AI backend.
    :raises AIHandlerException: Raised for specific error scenarios to be communicated to the front-end.
    """
    try:
        response = ai_backend.prompt_with_context(
            pre_prompt=pre_prompt, context=context
        )
    except Exception as e:
        # Raise a more generic error to send to the front-end
        raise AIHandlerException(
            "Error processing request, Please try again later."
        ) from e
    return response


def _replace_handler(*, prompt: Prompt, text: str) -> str:
    ai_backend = ai.get_ai_backend(alias="default")  # TODO update
    splitter = ai_backend.get_text_splitter()
    texts = splitter.split_text(text)

    for split in texts:
        response = _process_backend_request(
            ai_backend, pre_prompt=prompt.prompt_value, context=split
        )
        # Remove extra blank lines returned by the API
        message = os.linesep.join([s for s in response.text().splitlines() if s])
        text = text.replace(split, message)

    return text


def _append_handler(*, prompt: Prompt, text: str) -> str:
    ai_backend = ai.get_ai_backend(alias="default")  # TODO update
    length_calculator = ai_backend.get_splitter_length_calculator()
    if length_calculator.get_splitter_length(text) > ai_backend.config.token_limit:
        raise AIHandlerException("Cannot run completion on text this long")

    response = _process_backend_request(
        ai_backend, pre_prompt=prompt.prompt_value, context=text
    )
    # Remove extra blank lines returned by the API
    message = os.linesep.join([s for s in response.text().splitlines() if s])

    return message


@csrf_exempt
def process(request) -> JsonResponse:
    prompt_form = PromptForm(request.POST)

    if not prompt_form.is_valid():
        return JsonResponse(
            {"error": prompt_form.errors_for_json_response()}, status=400
        )

    try:
        prompt = Prompt.objects.get(uuid=prompt_form.cleaned_data["prompt"])
    except Prompt.DoesNotExist:
        return JsonResponse({"error": _("Invalid prompt provided.")}, status=400)

    handlers = {
        Prompt.Method.REPLACE: _replace_handler,
        Prompt.Method.APPEND: _append_handler,
    }

    handler = handlers[Prompt.Method(prompt.method)]

    try:
        response = handler(prompt=prompt, text=prompt_form.cleaned_data["text"])
    except AIHandlerException as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception:
        logger.exception("An unexpected error occurred.")
        return JsonResponse({"error": _("An unexpected error occurred.")}, status=500)

    return JsonResponse({"message": response})


class PromptEditForm(forms.ModelForm):
    """
    Custom form for the model admin to allow users to view and edit default prompts
    """

    class Meta:
        model = Prompt
        fields = ["label", "description", "prompt", "method"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.is_default:
            # Make the prompt field not required if it's a default prompt
            self.fields["prompt"].required = False
            # Populate the placeholder with the value from DEFAULT_PROMPTS
            self.fields["prompt"].widget.attrs[
                "placeholder"
            ] = self.instance.get_default_prompt_value()


class PromptViewSet(ModelViewSet):
    model = Prompt
    form_fields = PromptEditForm.Meta.fields
    list_display = ["label", "description", "method", UpdatedAtColumn()]  # type: ignore
    icon = "edit"
    add_to_settings_menu = True
    menu_order = 300

    def get_form_class(self, for_update=False):
        if for_update:
            return PromptEditForm
        return super().get_form_class(for_update)


prompt_viewset = PromptViewSet("prompt")
