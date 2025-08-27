from django import forms
from django.utils.functional import cached_property
from wagtail.admin.panels import FieldPanel
from wagtail.admin.staticfiles import versioned_static


class AIFieldPanel(FieldPanel):
    BASE_ATTRS = {
        **FieldPanel.BASE_ATTRS,
        "data-controller": " ".join(
            [FieldPanel.BASE_ATTRS.get("data-controller", ""), "wai-field-panel"]
        ).strip(),
    }

    class BoundPanel(FieldPanel.BoundPanel):
        template_name = "wagtail_ai/panels/field_panel.html"

        @cached_property
        def media(self):  # type: ignore
            return super().media + forms.Media(
                js=[versioned_static("wagtail_ai/field_panel.js")],
                css={"all": [versioned_static("wagtail_ai/field_panel.css")]},
            )
