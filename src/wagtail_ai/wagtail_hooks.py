import json

from django.urls import include, path, reverse
from django.utils.safestring import mark_safe
from django.views.i18n import JavaScriptCatalog
from wagtail import hooks
from wagtail.admin.rich_text.editors.draftail.features import ControlFeature

from .prompts import get_prompts
from .views import process


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
                'type': feature_name,
            },
            js=["wagtail_ai/wagtail-ai.js"],
            css={"all": ["wagtail_ai/main.css"]}
        ),
    )


@hooks.register("insert_editor_js")  # type: ignore
def ai_editor_js():
    prompt_json = json.dumps([prompt.as_dict() for prompt in get_prompts()])
    process_url = reverse("wagtail_ai:process")

    return mark_safe(
        f"""
        <script>
            window.WAGTAIL_AI_PROCESS_URL = "{process_url}";
            window.WAGTAIL_AI_PROMPTS = {prompt_json};
        </script>
        """
    )
