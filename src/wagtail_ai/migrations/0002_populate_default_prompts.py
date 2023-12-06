# Created using Django 4.2.7 on 2023-12-06 10:07

from django.db import migrations

from wagtail_ai.models import DEFAULT_PROMPTS


def set_default_ai_prompts(apps, schema_editor):
    """
    Loop through each default prompt and
    populate the database.
    """
    Prompt = apps.get_model("wagtail_ai", "Prompt")
    for default_prompt in DEFAULT_PROMPTS:
        Prompt.objects.update_or_create(
            uuid=default_prompt["uuid"],
            label=default_prompt["label"],
            prompt=None,  # Left blank to allow users to override the prompt value and maintainers of wagtail AI to manage the prompt in the codebase.
            description=default_prompt.get("description", ""),
            method=default_prompt.get("method", None),
        )


class Migration(migrations.Migration):
    dependencies = [
        ("wagtail_ai", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(set_default_ai_prompts, migrations.RunPython.noop),
    ]
