import logging
import os
from typing import Type, cast

from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.images.models import AbstractImage
from wagtail.images.permissions import get_image_model

from . import ai, types
from .ai.base import BackendFeature
from .forms import DescribeImageApiForm, PromptForm
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
    ai_backend = ai.get_backend()
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
    ai_backend = ai.get_backend()
    length_calculator = ai_backend.get_splitter_length_calculator()
    if length_calculator.get_splitter_length(text) > ai_backend.config.token_limit:
        raise AIHandlerException("Cannot run completion on text this long")

    response = _process_backend_request(
        ai_backend, pre_prompt=prompt.prompt_value, context=text
    )
    # Remove extra blank lines returned by the API
    message = os.linesep.join([s for s in response.text().splitlines() if s])

    return message


def ErrorJsonResponse(error_message, status=500):
    return JsonResponse({"error": error_message}, status=status)


@csrf_exempt
def text_completion(request) -> JsonResponse:
    prompt_form = PromptForm(request.POST)

    if not prompt_form.is_valid():
        return ErrorJsonResponse(prompt_form.errors_for_json_response(), status=400)

    try:
        prompt = Prompt.objects.get(uuid=prompt_form.cleaned_data["prompt"])
    except Prompt.DoesNotExist:
        return ErrorJsonResponse(_("Invalid prompt provided."), status=400)

    handlers = {
        Prompt.Method.REPLACE: _replace_handler,
        Prompt.Method.APPEND: _append_handler,
    }

    handler = handlers[Prompt.Method(prompt.method)]

    try:
        response = handler(prompt=prompt, text=prompt_form.cleaned_data["text"])
    except AIHandlerException as e:
        return ErrorJsonResponse(str(e), status=400)
    except Exception:
        logger.exception("An unexpected error occurred.")
        return ErrorJsonResponse(_("An unexpected error occurred."))

    return JsonResponse({"message": response})


def user_has_permission_for_image(user, image):
    from wagtail.images.permissions import permission_policy

    return permission_policy.user_has_permission_for_instance(user, "choose", image)


def describe_image(request) -> JsonResponse:
    form = DescribeImageApiForm(request.POST)
    if not form.is_valid():
        return ErrorJsonResponse(form.errors_for_json_response(), status=400)

    model = cast(Type[AbstractImage], get_image_model())
    image = get_object_or_404(model, pk=form.cleaned_data["image_id"])

    if not user_has_permission_for_image(request.user, image):
        return ErrorJsonResponse("Access denied", status=403)

    try:
        backend = ai.get_backend(BackendFeature.IMAGE_DESCRIPTION)
    except ai.BackendNotFound:
        return ErrorJsonResponse(
            "No backend is configured for image description. Please set"
            " `IMAGE_DESCRIPTION_BACKEND` in `settings.WAGTAIL_AI`.",
            status=400,
        )

    wagtail_ai_settings = getattr(settings, "WAGTAIL_AI", {})
    rendition_filter = wagtail_ai_settings.get(
        "IMAGE_DESCRIPTION_RENDITION_FILTER", "max-800x600"
    )
    rendition = image.get_rendition(rendition_filter)

    maxlength = form.cleaned_data["maxlength"]
    prompt = wagtail_ai_settings.get("IMAGE_DESCRIPTION_PROMPT")

    if prompt is None:
        prompt = (
            "Describe this image. Make the description suitable for use as an alt-text."
        )
        if maxlength is not None:
            prompt += f" Make the description less than {maxlength} characters long."

    try:
        ai_response = backend.describe_image(image_file=rendition.file, prompt=prompt)
        description = ai_response.text()
    except Exception:
        logger.exception("There was an issue describing the image.")
        return ErrorJsonResponse("There was an issue describing the image.")

    if not description:
        return ErrorJsonResponse("There was an issue describing the image.")

    if maxlength is not None:
        description = description[:maxlength]

    return JsonResponse({"message": description})


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
