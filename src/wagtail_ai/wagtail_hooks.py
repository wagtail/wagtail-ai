import uuid
from typing import NotRequired, Required, TypedDict

from django.urls import include, path, reverse
from django.utils.html import json_script
from django.utils.safestring import mark_safe
from django.views.i18n import JavaScriptCatalog
from wagtail import hooks
from wagtail.admin.rich_text.editors.draftail.features import ControlFeature

from .models import Prompt
from .views import process, prompt_viewset


@hooks.register("register_admin_urls")  # type: ignore
def register_admin_urls():
    urls = [
        path(
            "jsi18n/",
            JavaScriptCatalog.as_view(packages=["wagtail_ai"]),
            name="javascript_catalog",
        ),
        path(
            "process/",
            process,
            name="process",
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
            js=["wagtail_ai/wagtail-ai.js"],
            css={"all": ["wagtail_ai/main.css"]},
        ),
    )


class PromptDict(TypedDict):
    # Fields should match the Prompt type defined in custom.d.ts
    # be careful not to expose any sensitive or exploitable data here.
    uuid: Required[uuid.UUID]
    label: Required[str]
    description: NotRequired[str]
    prompt: Required[str]
    method: Required[str]


def _serialize_prompt(prompt: Prompt) -> PromptDict:
    return {
        "uuid": prompt.uuid,
        "label": prompt.label,
        "description": prompt.description,
        "prompt": prompt.prompt_value,
        "method": prompt.method,
    }


def get_prompts():
    return [_serialize_prompt(prompt) for prompt in Prompt.objects.all()]


@hooks.register("insert_editor_js")  # type: ignore
def ai_editor_js():
    prompt_json = get_prompts()
    process_url = reverse("wagtail_ai:process")

    wagtail_ai_config = json_script(
        {"aiPrompts": prompt_json, "aiProcessUrl": process_url},
        "wagtail-ai-config",
    )

    return mark_safe(wagtail_ai_config)


@hooks.register("register_admin_viewset")  # type: ignore
def register_viewset():
    return prompt_viewset
