from typing import Callable, TypeVar

from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_ai_core.llm.prompt import Prompt, TokenDict
from wagtail.contrib.settings.models import BaseGenericSetting

from .models import AgentSettings
from .models import CustomPrompt as CustomPromptModel

PromptT = TypeVar("PromptT", bound=Prompt)


class ManagedPromptRegistry:
    def __init__(self):
        self._prompts: dict[str, type[Prompt]] = {}

    def register(
        self, cls: type[PromptT] | None = None
    ) -> type[PromptT] | Callable[[type[PromptT]], type[PromptT]]:
        def decorator(prompt_cls: type[PromptT]) -> type[PromptT]:
            prompt_name = prompt_cls.__name__
            self._prompts[prompt_name] = prompt_cls
            return prompt_cls

        if cls is None:
            # Called with parentheses: @registry.register()
            return decorator
        else:
            # Called without parentheses: @registry.register
            return decorator(cls)

    def get(self, name: str) -> type[Prompt]:
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found")
        return self._prompts[name]

    def list(self) -> dict[str, type[Prompt]]:
        return self._prompts.copy()


registry = ManagedPromptRegistry()


DEFAULT_MANAGED_PROMPTS = {
    "TITLE": (
        "Create an SEO-friendly page title for the following web page content:\n\n"
        "{content_text}"
    ),
    "META_DESCRIPTION": (
        "Create an SEO-friendly meta description of the following web page content:\n\n"
        "{content_text}"
    ),
    "CONTEXTUAL_ALT_TEXT": (
        """Generate an alt text (and only the text) for the following image: {image_id}

Make the alt text relevant to the following content shown before the image:

---
{form_context_before}
---

and also relevant to the following content shown after the image:

---
{form_context_after}
---
"""
    ),
    "IMAGE_TITLE": (
        "Generate a title (and only the title, no longer than "
        "{max_length} characters) for the following image: {image_id}"
    ),
    "IMAGE_DESCRIPTION": (
        "Generate a description (and only the description, no longer than "
        "{max_length} characters) for the following image: {image_id}"
    ),
}


class WagtailAIPrompt(Prompt):
    name: str
    description: str
    method: str = "replace"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        registry.register(cls)


class SettingsManagedPrompt(WagtailAIPrompt):
    settings_model: type[BaseGenericSetting]
    prompt_field: str
    default_value: str

    def __new__(cls, **tokens):
        obj = super().__new__(cls, "", **tokens)
        return obj

    @cached_property
    def _base_text(self) -> str:
        """Lazily fetch the raw prompt string from settings."""
        settings = self.settings_model.load()
        value = getattr(settings, self.prompt_field)
        if value:
            return value
        return self.default_value

    def __str__(self) -> str:
        """Render using the lazy-loaded base text."""
        tokens = self._tokens
        return self._base_text.format_map(TokenDict(tokens))

    def with_tokens(self, **tokens) -> "SettingsManagedPrompt":
        """Return a new Prompt with overridden tokens."""
        merged = {**self._tokens, **tokens}
        new_prompt = type(self)(**merged)
        new_prompt.settings_model = self.settings_model
        new_prompt.prompt_field = self.prompt_field
        return new_prompt


class CustomPrompt(WagtailAIPrompt):
    uuid: str

    @cached_property
    def _base_text(self) -> str:
        """Lazily fetch the raw prompt string from the CustomPrompt."""
        prompt = CustomPrompt.objects.get(uuid=self.uuid)
        return prompt.prompt

    def __str__(self) -> str:
        """Render using the lazy-loaded base text."""
        tokens = self._tokens
        return self._base_text.format_map(TokenDict(tokens))

    @classmethod
    def from_model(cls, instance: CustomPromptModel):
        return type(
            "CustomPrompt",
            (cls,),
            {
                "uuid": instance.uuid,
                "name": instance.label,
                "description": instance.description,
                "method": instance.method,
            },
        )


class TitlePrompt(SettingsManagedPrompt):
    name = _("AI Title")
    description = _("Generate a title based on the page content")
    settings_model = AgentSettings
    prompt_field = "title_prompt"
    default_value = DEFAULT_MANAGED_PROMPTS["TITLE"]


class MetaDescriptionPrompt(SettingsManagedPrompt):
    name = _("AI Description")
    description = _("Generate a description by summarizing the page content")
    settings_model = AgentSettings
    prompt_field = "meta_description_prompt"
    default_value = DEFAULT_MANAGED_PROMPTS["META_DESCRIPTION"]


class ContextualAltTextPrompt(SettingsManagedPrompt):
    name = _("Contextual alt text")
    description = _("Generate an alt text for the image with the relevant context")
    settings_model = AgentSettings
    prompt_field = "contextual_alt_text_prompt"
    default_value = DEFAULT_MANAGED_PROMPTS["CONTEXTUAL_ALT_TEXT"]


class ImageTitlePrompt(SettingsManagedPrompt):
    name = _("Image title")
    description = _("Generate a title for the image")
    settings_model = AgentSettings
    prompt_field = "image_title_prompt"
    default_value = DEFAULT_MANAGED_PROMPTS["IMAGE_TITLE"]


class ImageDescriptionPrompt(SettingsManagedPrompt):
    name = _("Image description")
    description = _("Generate a description for the image")
    settings_model = AgentSettings
    prompt_field = "image_description_prompt"
    default_value = DEFAULT_MANAGED_PROMPTS["IMAGE_DESCRIPTION"]


def get_custom_prompts():
    return [CustomPrompt.from_model(prompt) for prompt in CustomPrompt.objects.all()]
