from django.apps import AppConfig


class WagtailAiAppConfig(AppConfig):
    label = "wagtail_ai"
    name = "wagtail_ai"
    verbose_name = "Wagtail AI"

    def ready(self) -> None:
        # Import for side effects.
        from . import signal_handlers  # noqa: F401
