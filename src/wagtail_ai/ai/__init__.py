import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from typing import NotRequired, Required, TypedDict, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from ..text_splitters.langchain import LangchainRecursiveCharacterTextSplitter
from ..text_splitters.length import NaiveTextSplitterCalculator
from ..types import TextSplitterLengthCalculatorProtocol, TextSplitterProtocol
from ..utils import deprecation
from .base import AIBackend, BackendFeature, BaseAIBackendConfigSettings


class TextSplittingSettingsDict(TypedDict):
    SPLITTER_CLASS: NotRequired[str]
    SPLITTER_LENGTH_CALCULATOR_CLASS: NotRequired[str]


class InvalidAIBackendError(ImproperlyConfigured):
    def __init__(self, alias):
        super().__init__(f"Invalid AI backend: {alias}")


class AIBackendSettingsDict(TypedDict):
    CONFIG: Required[BaseAIBackendConfigSettings]
    CLASS: Required[str]
    TEXT_SPLITTING: NotRequired[TextSplittingSettingsDict]


def get_ai_backends_settings() -> Mapping[str, AIBackendSettingsDict]:
    try:
        return settings.WAGTAIL_AI["BACKENDS"]
    except AttributeError:
        pass
    try:
        legacy_settings = settings.WAGTAIL_AI_BACKENDS
    except AttributeError:
        pass
    else:
        warnings.warn(
            'settings.WAGTAIL_AI_BACKENDS is deprecated. Please use "WAGTAIL_AI = {"BACKENDS": {"default": {...}}}" instead',
            deprecation.WagtailAISettingsDeprecationWarning,
            stacklevel=1,
        )
        return legacy_settings
    return {
        "default": {
            "CLASS": "wagtail_ai.ai.llm.LLMBackend",
            "CONFIG": {
                "MODEL_ID": "gpt-3.5-turbo",
            },
        }
    }


def _validate_backend_settings(*, settings: AIBackendSettingsDict, alias: str) -> None:
    if "CONFIG" not in settings:
        raise ImproperlyConfigured(
            'AI backend settings for "{alias}": Missing "CONFIG".'
        )
    if not isinstance(settings["CONFIG"], Mapping):
        raise ImproperlyConfigured(
            'AI backend settings for "{alias}": "CONFIG" is not a Mapping.'
        )
    if "MODEL_ID" not in settings["CONFIG"]:
        raise ImproperlyConfigured(
            'AI backend settings for "{alias}": "MODEL_ID" is missing in "CONFIG".'
        )


def get_ai_backend_settings(alias: str) -> AIBackendSettingsDict:
    backends_settings = get_ai_backends_settings()
    try:
        return backends_settings[alias]
    except (KeyError, ImportError) as e:
        raise InvalidAIBackendError(alias) from e

    _validate_backend_settings(settings=backends_settings, alias=alias)


def _get_default_text_splitter_class() -> type[LangchainRecursiveCharacterTextSplitter]:
    return LangchainRecursiveCharacterTextSplitter


def _get_default_text_splitter_length_class() -> type[NaiveTextSplitterCalculator]:
    return NaiveTextSplitterCalculator


@dataclass(kw_only=True)
class _TextSplitterConfig:
    splitter_class: type[TextSplitterProtocol]
    splitter_length_calculator_class: type[TextSplitterLengthCalculatorProtocol]


def _get_text_splitter_config(
    *, backend_alias: str, config: TextSplittingSettingsDict
) -> _TextSplitterConfig:
    splitter_class_path = config.get("SPLITTER_CLASS")
    length_calculator_class_path = config.get("SPLITTER_LENGTH_CALCULATOR_CLASS")

    # Text splitter - class that splits text into chunks of a given size.
    if splitter_class_path is not None:
        try:
            splitter_class = cast(
                type[TextSplitterProtocol], import_string(splitter_class_path)
            )
        except ImportError as e:
            raise ImproperlyConfigured(
                f'Cannot import "SPLITTER_CLASS" ("{splitter_class_path}") for backend "{backend_alias}".'
            ) from e
    else:
        splitter_class = _get_default_text_splitter_class()

    # Text splitter length calculator - class that calculates the number of token in a given text.
    if length_calculator_class_path is not None:
        try:
            length_calculator_class = cast(
                type[TextSplitterLengthCalculatorProtocol],
                import_string(length_calculator_class_path),
            )
        except ImportError as e:
            raise ImproperlyConfigured(
                f'Cannot import "SPLITTER_LENGTH_CALCULATOR_CLASS" ("{length_calculator_class_path}") for backend "{backend_alias}".'
            ) from e
    else:
        length_calculator_class = _get_default_text_splitter_length_class()

    return _TextSplitterConfig(
        splitter_class=splitter_class,
        splitter_length_calculator_class=length_calculator_class,
    )


def get_ai_backend(alias: str) -> AIBackend:
    backend_dict = get_ai_backend_settings(alias)

    if "CLASS" not in backend_dict:
        raise ImproperlyConfigured(
            f'"AI backend "{alias}" settings: "CLASS" is missing in the configuration.'
        )

    try:
        ai_backend_cls = cast(type[AIBackend], import_string(backend_dict["CLASS"]))
    except ImportError as e:
        raise InvalidAIBackendError(
            f'"AI backend "{alias}" settings: "CLASS" ("{backend_dict["CLASS"]}") is not importable.'
        ) from e

    backend_settings = backend_dict["CONFIG"]
    text_splitting = _get_text_splitter_config(
        backend_alias=alias,
        config=backend_dict.get("TEXT_SPLITTING", {}),
    )
    config = ai_backend_cls.config_cls.from_settings(
        backend_settings,
        text_splitter_class=text_splitting.splitter_class,
        text_splitter_length_calculator_class=text_splitting.splitter_length_calculator_class,
    )

    return ai_backend_cls(config=config)


class BackendNotFound(Exception):
    pass


def get_backend(feature: BackendFeature = BackendFeature.TEXT_COMPLETION) -> AIBackend:
    match feature:
        case BackendFeature.TEXT_COMPLETION:
            alias = settings.WAGTAIL_AI.get("TEXT_COMPLETION_BACKEND", "default")
        case BackendFeature.IMAGE_DESCRIPTION:
            alias = settings.WAGTAIL_AI.get("IMAGE_DESCRIPTION_BACKEND")
        case _:
            alias = None

    if alias is None:
        raise BackendNotFound(f"No backend found for {feature.name}")

    return get_ai_backend(alias)
