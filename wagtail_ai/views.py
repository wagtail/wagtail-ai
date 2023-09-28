import os

import tiktoken
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .ai_backends import get_ai_backend
from .prompts import Prompt, get_prompt_by_id

DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 4096


class AIHandlerException(Exception):
    pass


def _splitter_length(string):
    """Return the number of tokens in a string, used by the Langchain
    splitter so we split based on tokens rather than characters."""
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL)
    return len(encoding.encode(string))


def _replace_handler(prompt: Prompt, text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_MAX_TOKENS, length_function=_splitter_length
    )
    texts = splitter.split_text(text)

    for split in texts:
        full_prompt = "\n".join([prompt.prompt, split])
        backend = get_ai_backend()
        message = backend.prompt(user_messages=[full_prompt])
        # Remove extra blank lines returned by the API
        message = os.linesep.join([s for s in message.splitlines() if s])
        text = text.replace(split, message)

    return text


def _append_handler(prompt: Prompt, text: str):
    tokens = _splitter_length(text)
    if tokens > DEFAULT_MAX_TOKENS:
        raise AIHandlerException("Cannot run completion on text this long")

    full_prompt = "\n".join([prompt.prompt, text])
    backend = get_ai_backend()
    message = backend.prompt(user_messages=[full_prompt])
    # Remove extra blank lines returned by the API
    message = os.linesep.join([s for s in message.splitlines() if s])

    return message


@csrf_exempt
def process(request):
    text = request.POST.get("text")
    prompt_idx = request.POST.get("prompt")
    prompt = get_prompt_by_id(int(prompt_idx))

    if not text:
        return JsonResponse(
            {
                "error": "No text provided - please enter some text before using AI \
                    features"
            },
            status=400,
        )

    if not prompt:
        return JsonResponse({"error": "Invalid prompt provided"}, status=400)

    handlers = {
        Prompt.Method.REPLACE: _replace_handler,
        Prompt.Method.APPEND: _append_handler,
    }

    handler = handlers[prompt.method]
    try:
        response = handler(prompt, text)
    except AIHandlerException as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": response})
