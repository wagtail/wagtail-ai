from django.apps import AppConfig


class WagtailAiAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    label = "wagtail_ai"
    name = "wagtail_ai"
    verbose_name = "Wagtail AI"

    def ready(self) -> None:
        # Import for side effects.
        from . import signal_handlers  # noqa: F401
