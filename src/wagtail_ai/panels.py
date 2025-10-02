import json

from django import forms
from django.utils.functional import cached_property, classproperty  # type: ignore
from wagtail.admin.panels import (
    FieldPanel,
    MultipleChooserPanel,
    Panel,
    TitleFieldPanel,
)
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


class AIMultipleChooserPanel(MultipleChooserPanel):
    def __init__(self, *args, suggest_limit=3, **kwargs):
        super().__init__(*args, **kwargs)
        self.suggest_limit = 3

    @classproperty
    def BASE_ATTRS(cls):
        base = super().BASE_ATTRS
        controllers = [base.get("data-controller", ""), "wai-multiple-chooser-panel"]
        return {
            **base,
            "data-controller": " ".join(controllers).strip(),
        }

    class BoundPanel(MultipleChooserPanel.BoundPanel):
        template_name = "wagtail_ai/panels/ai_multiple_chooser_panel.html"

        @property
        def attrs(self):
            attrs = super().attrs
            attrs["data-wai-multiple-chooser-panel-instance-pk-value"] = (
                self.instance.pk
            )
            attrs["data-wai-multiple-chooser-panel-suggest-limit-value"] = (
                self.panel.suggest_limit
            )
            return attrs

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context=parent_context)
            context["parent_prefix"] = self.prefix.replace("content-child-", "content-")
            return context

        @cached_property
        def media(self):  # type: ignore
            return super().media + forms.Media(
                js=[versioned_static("wagtail_ai/multiple_chooser_panel.js")],
                css={
                    "all": [versioned_static("wagtail_ai/multiple_chooser_panel.css")]
                },
            )
