import logging
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import ai, prompts

logger = logging.getLogger(__name__)


class AIHandlerException(Exception):
    pass


def _replace_handler(*, prompt: prompts.Prompt, text: str) -> str:
    ai_backend = ai.get_ai_backend(alias=prompt.backend)
    splitter = ai_backend.get_text_splitter()
    texts = splitter.split_text(text)

    for split in texts:
        response = ai_backend.prompt_with_context(
            pre_prompt=prompt.prompt, context=split
        )
        # Remove extra blank lines returned by the API
        message = os.linesep.join([s for s in response.text().splitlines() if s])
        text = text.replace(split, message)

    return text


def _append_handler(*, prompt: prompts.Prompt, text: str) -> str:
    ai_backend = ai.get_ai_backend(alias=prompt.backend)
    length_calculator = ai_backend.get_splitter_length_calculator()
    if length_calculator.get_splitter_length(text) > ai_backend.config.token_limit:
        raise AIHandlerException("Cannot run completion on text this long")

    response = ai_backend.prompt_with_context(pre_prompt=prompt.prompt, context=text)
    # Remove extra blank lines returned by the API
    message = os.linesep.join([s for s in response.text().splitlines() if s])

    return message


@csrf_exempt
def process(request):
    text = request.POST.get("text")

    if not text:
        return JsonResponse(
            {
                "error": "No text provided - please enter some text before using AI \
                    features"
            },
            status=400,
        )

    prompt_idx = request.POST.get("prompt")

    try:
        prompt = prompts.get_prompt_by_id(int(prompt_idx))
    except prompts.Prompt.DoesNotExist:
        return JsonResponse({"error": "Invalid prompt provided"}, status=400)

    handlers = {
        prompts.Prompt.Method.REPLACE: _replace_handler,
        prompts.Prompt.Method.APPEND: _append_handler,
    }

    handler = handlers[prompts.Prompt.Method(prompt.method)]

    try:
        response = handler(prompt=prompt, text=text)
    except AIHandlerException as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception:
        logger.exception("An unexpected error occurred.")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)

    return JsonResponse({"message": response})
