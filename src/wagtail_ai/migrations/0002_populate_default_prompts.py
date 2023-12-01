# Generated using Django 4.2.7 on 2023-12-01 09:35

from django.conf import settings
from django.db import migrations

import wagtail_ai


def set_default_ai_prompts(apps, schema_editor):
    """
    Loop through each default prompt in settings and
    create instances in the database.
    """
    Prompt = apps.get_model("wagtail_ai", "Prompt")

    default_prompts = (
        wagtail_ai.DEFAULT_PROMPTS if hasattr(wagtail_ai, "DEFAULT_PROMPTS") else []
    )

    for default_prompt in (
        getattr(settings, "WAGTAIL_AI_PROMPTS", []) or default_prompts
    ):
        Prompt.objects.create(
            label=default_prompt["label"],
            prompt=default_prompt["prompt"],
            description=default_prompt.get("description", ""),
            method=default_prompt.get("method", None),
        )


def reverse_set_default_ai_prompts(apps, schema_editor):
    """
    Reverse the migration by deleting all instances of the Prompt model.
    """
    Prompt = apps.get_model("wagtail_ai", "Prompt")
    Prompt.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("wagtail_ai", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            set_default_ai_prompts, reverse_code=reverse_set_default_ai_prompts
        ),
    ]
