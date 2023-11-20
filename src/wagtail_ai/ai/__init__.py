from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, NotRequired, Required, TypedDict, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .. import tokens
from ..text_splitters.base import BaseTextSplitterLength
from ..text_splitters.langchain import LangchainRecursiveCharacterTextSplitter
from ..text_splitters.length import NaiveTextSplitterLength
from ..types import TextSplitterProtocol
from .base import AIBackend, ChatModelConfig


class InvalidAIBackendError(ImproperlyConfigured):
    def __init__(self, alias):
        super().__init__(f"Invalid AI backend: {alias}")


class TextSplitterSettings(TypedDict):
    TEXT_SPLITTER_CLASS: NotRequired[str | None]
    TEXT_SPLITTER_LENGTH_CLASS: NotRequired[str | None]


class ChatModelSettings(TypedDict):
    ID: Required[str]
    TOKEN_LIMIT: NotRequired[int | None]
    TEXT_SPLITTING: NotRequired[TextSplitterSettings | None]
    EXTRA: NotRequired[Mapping[str, Any] | None]


class AIBackendSettings(TypedDict):
    CHAT_MODEL: Required[ChatModelSettings]
    CLASS: Required[str]
    CONFIG: NotRequired[Any]


def get_ai_backends_settings() -> Mapping[str, AIBackendSettings]:
    try:
        return settings.WAGTAIL_AI["BACKENDS"]
    except AttributeError:
        return {
            "default": {
                "CLASS": "wagtail_ai.ai.llm.LLMBackend",
                "CHAT_MODEL": {
                    "ID": "gpt-3.5-turbo",
                },
            }
        }


def get_ai_backend_settings(alias: str) -> AIBackendSettings:
    backends_config = get_ai_backends_settings()
    try:
        return backends_config[alias]
    except (KeyError, ImportError) as e:
        raise InvalidAIBackendError(alias) from e


def _get_default_text_splitter_class() -> type[LangchainRecursiveCharacterTextSplitter]:
    return LangchainRecursiveCharacterTextSplitter


def _get_default_text_splitter_length_class() -> type[NaiveTextSplitterLength]:
    return NaiveTextSplitterLength


def _get_chat_model_config(chat_model: ChatModelSettings) -> ChatModelConfig:
    text_splitter = _get_text_splitter_config(chat_model=chat_model)

    return ChatModelConfig(
        extra=chat_model.get("EXTRA"),
        id=chat_model["ID"],
        text_splitter_class=text_splitter.splitter_class,
        text_splitter_length_class=text_splitter.length_class,
        token_limit=text_splitter.token_limit,
    )


@dataclass(kw_only=True)
class _TextSplitterConfig:
    splitter_class: type[TextSplitterProtocol]
    length_class: type[BaseTextSplitterLength]
    token_limit: int


def _get_text_splitter_config(chat_model: ChatModelSettings) -> _TextSplitterConfig:
    model_id = chat_model["ID"]
    token_limit = chat_model.get("TOKEN_LIMIT")
    splitter_class_path = chat_model.get("TEXT_SPLITTER_CLASS")
    length_class_path = chat_model.get("TEXT_SPLITTER_LENGTH_CLASS")

    # Token limit - how many tokens can be sent in one request to the model.
    if token_limit is None:
        try:
            token_limit = tokens.get_default_token_limit(chat_model["ID"])
        except tokens.NoTokenLimitFound as e:
            raise ImproperlyConfigured(
                f'You need to specify "TOKEN_LIMIT" inside the "CHAT_MODEL" setting for model "{model_id}".'
            ) from e

    # Text splitter - function that splits text into chunks of a given size.
    if splitter_class_path is not None:
        try:
            splitter_class = import_string(splitter_class_path)
        except ImportError as e:
            raise ImproperlyConfigured(
                f'Cannot import "TEXT_SPLITTER_CLASS" ("{splitter_class_path}") for model "{model_id}".'
            ) from e
    else:
        splitter_class = _get_default_text_splitter_class()

    # Text splitter length - function that calculates the number of token in a given text.
    if length_class_path is not None:
        try:
            length_class = import_string(length_class_path)
        except ImportError as e:
            raise ImproperlyConfigured(
                f'Cannot import "TEXT_SPLITTER_LENGTH_CLASS" ("{length_class_path}") for model "{model_id}".'
            ) from e
    else:
        length_class = _get_default_text_splitter_length_class()

    return _TextSplitterConfig(
        splitter_class=splitter_class,
        length_class=length_class,
        token_limit=token_limit,
    )


def get_ai_backend(alias: str) -> AIBackend:
    backend_dict = get_ai_backend_settings(alias)

    try:
        ai_backend_cls = cast(type[AIBackend], import_string(backend_dict["CLASS"]))
    except (KeyError, ImportError) as e:
        raise InvalidAIBackendError(alias) from e

    chat_model_config = _get_chat_model_config(backend_dict["CHAT_MODEL"])

    return ai_backend_cls(
        config=backend_dict.get("CONFIG"), chat_model_config=chat_model_config
    )
