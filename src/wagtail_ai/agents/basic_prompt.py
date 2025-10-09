import base64
from abc import ABC
from urllib.parse import SplitResult

from django.conf import settings
from django.core.files import File
from django.utils.translation import gettext_lazy as _
from django_ai_core.contrib.agents import Agent, AgentParameter, registry

from wagtail_ai.context import PromptContext

from .base import get_llm_service

# Temporary drop-in for the Prompt model using prompts from AgentSettings


class SettingPrompt(ABC):
    name: str
    label: str
    description: str


class PageTitlePrompt(SettingPrompt):
    name = "page_title_prompt"
    label = _("Generate title")
    description = _("Generate a title based on the page content")


class PageDescriptionPrompt(SettingPrompt):
    name = "page_description_prompt"
    label = _("Generate description")
    description = _("Generate a description by summarizing the page content")


class ImageTitlePrompt(SettingPrompt):
    name = "image_title_prompt"
    label = _("Generate title")
    description = _("Generate a title for the image")


class ImageDescriptionPrompt(SettingPrompt):
    name = "image_description_prompt"
    label = _("Generate description")
    description = _("Generate a description for the image")


class ContextualAltTextPrompt(SettingPrompt):
    name = "contextual_alt_text_prompt"
    label = _("Generate alt text")
    description = _("Generate contextual alt text for the image")


@registry.register()
class BasicPromptAgent(Agent):
    slug = "wai_basic_prompt"
    description = (
        "Provides suggestions to an input field based on a given prompt and context."
    )
    parameters = [
        AgentParameter(
            name="prompt",
            type=str,
            description="The prompt to guide the suggestion.",
        ),
        AgentParameter(
            name="context",
            type=dict[str, str],
            description="Additional context to replace placeholders in the prompt text.",
        ),
    ]
    settings_prompts = [
        PageTitlePrompt,
        PageDescriptionPrompt,
        ImageTitlePrompt,
        ImageDescriptionPrompt,
        ContextualAltTextPrompt,
    ]
    provider_alias = "default"

    def execute(self, prompt: str, context: dict[str, str]) -> str:
        self.prompt = prompt
        self.context = self.validate_context(prompt, context)
        if self.context.get("image"):
            ai_settings = getattr(settings, "WAGTAIL_AI", {})
            self.provider_alias = ai_settings.get(
                "IMAGE_DESCRIPTION_PROVIDER", "default"
            )

        messages = self._get_prompt_messages()
        result = self._get_result(messages)
        return result

    def _get_prompt_messages(self):
        files = self.split_context_files()
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self.get_formatted_prompt(),
                    },
                    *files,
                ],
            },
        ]
        return messages

    def _get_result(self, messages: list[dict]) -> str:
        llm_service = get_llm_service(alias=self.provider_alias)
        result = llm_service.completion(messages=messages)
        return result.choices[0].message.content  # type: ignore

    def validate_context(self, prompt: str, context: dict[str, str]) -> PromptContext:
        context = PromptContext(context)
        context.clean(prompt)
        return context

    def get_formatted_prompt(self) -> str:
        return self.prompt.format_map(self.context)

    def split_context_files(self) -> list[File]:
        files = []
        for key, value in self.context.items():
            if isinstance(value, (File, SplitResult)):
                if isinstance(value, File):
                    # TODO: check the file type and handle accordingly
                    with value.open() as f:
                        base64_image = base64.b64encode(f.read()).decode()
                    url = f"data:image/jpeg;base64,{base64_image}"
                else:
                    # Assume it's a data URL for an image
                    url = value.geturl()
                files.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": url},
                    }
                )
                self.context[key] = f"[file {len(files)}]"
        return files
