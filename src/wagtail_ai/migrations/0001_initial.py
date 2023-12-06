# Generated by Django 4.2.7 on 2023-12-05 16:56

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Prompt",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("label", models.CharField(max_length=255)),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        help_text="The prompt description, displayed alongside its label on the settings listing.",
                        max_length=255,
                    ),
                ),
                (
                    "prompt",
                    models.TextField(
                        help_text="The prompt text sent to the Large Language Model (e.g. ChatGPT) to generate content.",
                        null=True,
                    ),
                ),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("replace", "Replace content"),
                            ("append", "Append after existing content"),
                        ],
                        help_text="The method used for processing the responses to the prompt.",
                        max_length=25,
                    ),
                ),
            ],
        ),
    ]
