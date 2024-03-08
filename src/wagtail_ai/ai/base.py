from abc import ABCMeta
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Generic,
    NotRequired,
    Protocol,
    Required,
    Self,
    TypedDict,
    TypeVar,
)

from django.core.exceptions import ImproperlyConfigured
from django.core.files import File

from .. import tokens
from ..types import (
    AIResponse,
    TextSplitterLengthCalculatorProtocol,
    TextSplitterProtocol,
)


class BackendFeature(Enum):
    TEXT_COMPLETION = "TEXT_COMPLETION"
    IMAGE_DESCRIPTION = "IMAGE_DESCRIPTION"


class BaseAIBackendConfigSettings(TypedDict):
    MODEL_ID: Required[str]
    TOKEN_LIMIT: NotRequired[int | None]


AIBackendConfigSettings = TypeVar(
    "AIBackendConfigSettings", bound=BaseAIBackendConfigSettings, contravariant=True
)


class ConfigClassProtocol(Protocol[AIBackendConfigSettings]):
    @classmethod
    def from_settings(cls, config: AIBackendConfigSettings, **kwargs: Any) -> Self:
        ...


@dataclass(kw_only=True)
class BaseAIBackendConfig(ConfigClassProtocol[AIBackendConfigSettings]):
    model_id: str
    token_limit: int
    text_splitter_class: type[TextSplitterProtocol]
    text_splitter_length_calculator_class: type[TextSplitterLengthCalculatorProtocol]

    @classmethod
    def from_settings(
        cls,
        config: AIBackendConfigSettings,
        *,
        text_splitter_class: type[TextSplitterProtocol],
        text_splitter_length_calculator_class: type[
            TextSplitterLengthCalculatorProtocol
        ],
        **kwargs: Any,
    ) -> Self:
        token_limit = cls.get_token_limit(
            model_id=config["MODEL_ID"], custom_value=config.get("TOKEN_LIMIT")
        )

        return cls(
            model_id=config["MODEL_ID"],
            token_limit=token_limit,
            text_splitter_class=text_splitter_class,
            text_splitter_length_calculator_class=text_splitter_length_calculator_class,
            **kwargs,
        )

    @classmethod
    def get_token_limit(cls, *, model_id: str, custom_value: int | None) -> int:
        if custom_value is not None:
            try:
                return int(custom_value)
            except ValueError as e:
                raise ImproperlyConfigured(
                    f'"TOKEN_LIMIT" is not an "int", it is a "{type(custom_value)}".'
                ) from e
        try:
            return tokens.get_default_token_limit(model_id=model_id)
        except tokens.NoTokenLimitFound as e:
            raise ImproperlyConfigured(
                f'"TOKEN_LIMIT" is not configured for model "{model_id}".'
            ) from e


AIBackendConfig = TypeVar("AIBackendConfig", bound=BaseAIBackendConfig)


class AIBackend(Generic[AIBackendConfig], metaclass=ABCMeta):
    config_cls: ClassVar[type[ConfigClassProtocol]]
    config: AIBackendConfig

    def __init__(
        self,
        *,
        config: AIBackendConfig,
    ) -> None:
        self.config = config

    def prompt_with_context(
        self, *, pre_prompt: str, context: str, post_prompt: str | None = None
    ) -> AIResponse:
        """
        Given a prompt and a context, return a response.
        """
        raise NotImplementedError("This backend does not support text completion")

    def get_text_splitter(self) -> TextSplitterProtocol:
        return self.config.text_splitter_class(
            chunk_size=self.config.token_limit,
            length_function=self.get_splitter_length_calculator().get_splitter_length,
        )

    def get_splitter_length_calculator(self) -> TextSplitterLengthCalculatorProtocol:
        return self.config.text_splitter_length_calculator_class()

    def describe_image(self, *, image_file: File, prompt: str) -> AIResponse:
        raise NotImplementedError("This backend does not support image description")
