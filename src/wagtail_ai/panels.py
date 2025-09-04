from django import forms
from django.utils.functional import cached_property, classproperty  # type: ignore
from wagtail.admin.panels import FieldPanel, Panel, TitleFieldPanel
from wagtail.admin.staticfiles import versioned_static


class AIPanelMixin(Panel):
    @classproperty
    def BASE_ATTRS(cls):
        base = super().BASE_ATTRS
        controllers = [base.get("data-controller", ""), "wai-field-panel"]
        return {
            **base,
            "data-controller": " ".join(controllers).strip(),
        }

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtail_ai/panels/field_panel.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            context["original_template_name"] = super().template_name  # type: ignore
            return context

        @cached_property
        def media(self):  # type: ignore
            return super().media + forms.Media(
                js=[versioned_static("wagtail_ai/field_panel.js")],
                css={"all": [versioned_static("wagtail_ai/field_panel.css")]},
            )


class AIFieldPanel(AIPanelMixin, FieldPanel):
    class BoundPanel(AIPanelMixin.BoundPanel, FieldPanel.BoundPanel):  # type: ignore
        pass


class AITitleFieldPanel(AIPanelMixin, TitleFieldPanel):
    class BoundPanel(AIPanelMixin.BoundPanel, TitleFieldPanel.BoundPanel):  # type: ignore
        pass
