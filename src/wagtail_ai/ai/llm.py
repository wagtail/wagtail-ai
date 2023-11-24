import os
from collections.abc import Mapping
from typing import Any, NotRequired, Self

import llm
from llm.models import dataclass

from ..types import AIResponse
from .base import AIBackend, BaseAIBackendConfig, BaseAIBackendConfigSettings


class LLMBackendConfigSettingsDict(BaseAIBackendConfigSettings):
    PROMPT_KWARGS: NotRequired[Mapping[str, Any] | None]
    INIT_KWARGS: NotRequired[Mapping[str, Any] | None]


@dataclass(kw_only=True)
class LLMBackendConfig(BaseAIBackendConfig[LLMBackendConfigSettingsDict]):
    prompt_kwargs: Mapping[str, Any]
    init_kwargs: Mapping[str, Any]

    @classmethod
    def from_settings(cls, config: LLMBackendConfigSettingsDict, **kwargs: Any) -> Self:
        init_kwargs = config.get("INIT_KWARGS")
        if init_kwargs is None:
            init_kwargs = {}
        kwargs.setdefault("init_kwargs", init_kwargs)

        prompt_kwargs = config.get("PROMPT_KWARGS")
        if prompt_kwargs is None:
            prompt_kwargs = {}
        kwargs.setdefault("prompt_kwargs", prompt_kwargs)

        return super().from_settings(config, **kwargs)


class LLMBackend(AIBackend[LLMBackendConfig]):
    config_cls = LLMBackendConfig

    def prompt_with_context(
        self, *, pre_prompt: str, context: str, post_prompt: str | None = None
    ) -> AIResponse:
        model = self.get_llm_model()
        parts = [pre_prompt, context]

        if post_prompt is not None:
            parts.append(post_prompt)

        full_prompt = os.linesep.join(parts)
        prompt_kwargs = {}
        if self.config.prompt_kwargs is not None:
            prompt_kwargs.update(self.config.prompt_kwargs)
        return model.prompt(full_prompt, **prompt_kwargs)

    def get_llm_model(self) -> llm.Model:
        model = llm.get_model(self.config.model_id)
        if self.config.init_kwargs is not None:
            for config_key, config_val in self.config.init_kwargs.items():
                setattr(model, config_key, config_val)
        return model
