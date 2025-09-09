import json

from django import forms
from django.utils.functional import cached_property, classproperty  # type: ignore
from wagtail.admin.panels import FieldPanel, Panel, TitleFieldPanel
from wagtail.admin.staticfiles import versioned_static


class AIPanelMixin(Panel):
    def __init__(self, *args, prompts=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompts = prompts or []
        self.attrs["data-wai-field-panel-prompts-value"] = json.dumps(self.prompts)

    @classproperty
    def BASE_ATTRS(cls):
        base = super().BASE_ATTRS
        controllers = [base.get("data-controller", ""), "wai-field-panel"]
        return {
            **base,
            "data-controller": " ".join(controllers).strip(),
        }

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs["prompts"] = self.prompts
        return kwargs

    class BoundPanel(Panel.BoundPanel):
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
