# Created using Django 4.2.7 on 2023-12-08 09:39

from django.db import migrations

from wagtail_ai.prompts import DEFAULT_PROMPTS


def set_default_ai_prompts(apps, schema_editor):
    """
    Loop through each default prompt and
    populate the database.
    """
    Prompt = apps.get_model("wagtail_ai", "Prompt")
    for default_prompt in DEFAULT_PROMPTS:
        Prompt.objects.update_or_create(
            default_prompt_id=default_prompt["default_prompt_id"],
            # The prompt field is left blank to allow users to override default prompt values and maintainers
            # to manage default prompts that are None (not overridden) using the get_default_prompt_value method.
            prompt=None,
            defaults={
                "label": default_prompt["label"],
                "description": default_prompt.get("description", ""),
                "method": default_prompt.get("method", None),
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("wagtail_ai", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(set_default_ai_prompts, migrations.RunPython.noop),
    ]
