import uuid
from typing import NotRequired, Required, TypedDict, cast

from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.urls import include, path, reverse
from django.utils.html import format_html, json_script
from django.views.i18n import JavaScriptCatalog
from django_ai_core.contrib.agents import registry
from wagtail import hooks
from wagtail.admin.rich_text.editors.draftail.features import ControlFeature
from wagtail.admin.staticfiles import versioned_static
from wagtail.contrib.settings.models import register_setting

from wagtail_ai.agents.base import get_agent_settings, get_agent_settings_model
from wagtail_ai.agents.basic_prompt import BasicPromptAgent

from .models import Prompt
from .views import describe_image, prompt_viewset, text_completion


@hooks.register("register_admin_urls")  # type: ignore
def register_admin_urls():
    content_feedback_agent = registry.get("wai_content_feedback")
    basic_prompt_agent = registry.get("wai_basic_prompt")
    suggested_content_agent = registry.get("wai_suggested_content")

    urls = [
        path(
            "jsi18n/",
            JavaScriptCatalog.as_view(packages=["wagtail_ai"]),
            name="javascript_catalog",
        ),
        path(
            "text_completion/",
            text_completion,
            name="text_completion",
        ),
        path(
            "describe_image/",
            describe_image,
            name="describe_image",
        ),
        path(
            "content_feedback/",
            content_feedback_agent.as_view(),
            name="content_feedback",
        ),
        path(
            "basic_prompt/",
            basic_prompt_agent.as_view(),
            name="basic_prompt",
        ),
        path(
            "suggested_content/",
            suggested_content_agent.as_view(),
            name="suggested_content",
        ),
    ]

    return [
        path(
            "ai/",
            include(
                (urls, "wagtail_ai"),
                namespace="wagtail_ai",
            ),
        )
    ]


@hooks.register("register_rich_text_features")  # type: ignore
def register_ai_feature(features):
    feature_name = "ai"
    features.default_features.append(feature_name)

    features.register_editor_plugin(
        "draftail",
        feature_name,
        ControlFeature(
            {
                "type": feature_name,
            },
            js=["wagtail_ai/draftail.js"],
            css={"all": ["wagtail_ai/draftail.css"]},
        ),
    )


class PromptDict(TypedDict):
    # Fields should match the Prompt type defined in custom.d.ts
    # be careful not to expose any sensitive or exploitable data here.
    uuid: Required[uuid.UUID]
    default_prompt_id: NotRequired[int | None]
    label: Required[str]
    description: NotRequired[str]
    prompt: Required[str]
    method: Required[str]


def _serialize_prompt(prompt: Prompt) -> PromptDict:
    return {
        "uuid": prompt.uuid,
        "default_prompt_id": prompt.default_prompt_id,
        "label": prompt.label,
        "description": prompt.description,
        "prompt": prompt.prompt_value,
        "method": prompt.method,
    }


def get_prompts():
    return [_serialize_prompt(prompt) for prompt in Prompt.objects.all()]


def get_setting_prompts():
    settings = get_agent_settings()
    basic_prompt_agent = cast(
        type[BasicPromptAgent],
        registry.get("wai_basic_prompt"),
    )
    return [
        {
            "name": prompt.name,
            "label": prompt.label,
            "description": prompt.description,
            "prompt": getattr(settings, prompt.name),
        }
        for prompt in basic_prompt_agent.settings_prompts
    ]


@hooks.register("insert_global_admin_css")  # type: ignore
def ai_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', versioned_static("wagtail_ai/main.css")
    )


@hooks.register("insert_global_admin_js")  # type: ignore
def ai_admin_js():
    config = {
        "aiPrompts": get_prompts(),
        "settingPrompts": get_setting_prompts(),
        "urls": {
            "TEXT_COMPLETION": reverse("wagtail_ai:text_completion"),
            "DESCRIBE_IMAGE": reverse("wagtail_ai:describe_image"),
            "CONTENT_FEEDBACK": reverse("wagtail_ai:content_feedback"),
            "BASIC_PROMPT": reverse("wagtail_ai:basic_prompt"),
            "SUGGESTED_CONTENT": reverse("wagtail_ai:suggested_content"),
        },
    }

    return format_html(
        '{}<script src="{}"></script>',
        json_script(config, "wagtail-ai-config"),
        versioned_static("wagtail_ai/main.js"),
    )


@hooks.register("insert_global_admin_js")  # type: ignore
def ai_editor_js():
    dropdown_attrs = {
        "data-wai-field-panel-target": "dropdown",
    }
    context = {
        "dropdown_attrs": flatatt(dropdown_attrs),
    }
    return render_to_string("wagtail_ai/shared/field_panel_dropdown.html", context)


@hooks.register("register_admin_viewset")  # type: ignore
def register_viewset():
    return prompt_viewset


@hooks.register("register_icons")  # type: ignore
def register_icons(icons):
    return [
        *icons,
        "wagtail_ai/icons/wand.svg",
        "wagtail_ai/icons/wand-animated.svg",
    ]


register_setting(get_agent_settings_model(), order=prompt_viewset.menu_order - 1)
