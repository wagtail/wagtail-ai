import os
from collections.abc import Mapping
from typing import Any

import llm

from .base import AIBackend, ChatModelConfig


class LLMBackend(AIBackend[None, ChatModelConfig]):
    llm_model_prompt_params: Mapping[str, Any] | None = None
    llm_model_init_kwargs: Mapping[str, Any] | None = None

    def init_config(
        self, *, backend_config: None, chat_model_config: ChatModelConfig
    ) -> None:
        if chat_model_config["extra"] is not None:
            self.llm_model_prompt_params = chat_model_config["extra"].get(
                "prompt_params"
            )
            self.llm_model_init_kwargs = chat_model_config["extra"].get("init_kwargs")

    def prompt(self, *, prompt: str, content: str, **kwargs: Any) -> llm.Response:
        model = self.get_llm_model()
        full_prompt = os.linesep.join([prompt, content])

        if self.llm_model_prompt_params is not None:
            for param_key, param_val in self.llm_model_prompt_params.items():
                kwargs.setdefault(param_key, param_val)

        return model.prompt(full_prompt, **kwargs)

    def get_llm_model(self) -> llm.Model:
        model = llm.get_model(self.chat_model_config["id"])
        if self.llm_model_init_kwargs is not None:
            for config_key, config_val in self.llm_model_init_kwargs.items():
                setattr(model, config_key, config_val)
        return model
