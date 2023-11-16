import os
from collections.abc import Mapping
from typing import Any, NotRequired, Required, TypedDict

import llm

from .base import AIBackend


class LLMBackendConfig(TypedDict):
    MODEL_ID: Required[str]
    MODEL_CONFIG: NotRequired[Mapping[str, Any]]
    PROMPT_PARAMS: NotRequired[Mapping[str, Any]]


class LLMBackend(AIBackend[LLMBackendConfig]):
    llm_model_id: str
    llm_model_config: Mapping[str, Any] | None
    llm_prompt_params: Mapping[str, Any] | None

    def init_config(self, config: LLMBackendConfig) -> None:
        self.llm_model_id = config["MODEL_ID"]
        self.llm_model_config = config.get("MODEL_CONFIG")
        self.llm_prompt_params = config.get("PROMPT_PARAMS")

    def prompt(self, *, prompt: str, content: str, **kwargs: Any) -> llm.Response:
        model = self.get_llm_model()
        full_prompt = os.linesep.join([prompt, content])

        if self.llm_prompt_params is not None:
            for param_key, param_val in self.llm_prompt_params.items():
                kwargs.setdefault(param_key, param_val)

        return model.prompt(full_prompt, **kwargs)

    def get_llm_model(self) -> llm.Model:
        model = llm.get_model(self.llm_model_id)
        if self.llm_model_config is not None:
            for config_key, config_val in self.llm_model_config.items():
                setattr(model, config_key, config_val)
        return model
