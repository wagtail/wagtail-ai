import json
from typing import TYPE_CHECKING

from django import forms
from django.utils.functional import cached_property, classproperty  # type: ignore
from wagtail.admin.panels import (
    FieldPanel,
    MultipleChooserPanel,
    Panel,
    TitleFieldPanel,
)
from wagtail.admin.staticfiles import versioned_static

from wagtail_ai.agents.basic_prompt import PageDescriptionPrompt, PageTitlePrompt

if TYPE_CHECKING:
    from django_ai_core.contrib.index import VectorIndex


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
    def __init__(self, *args, prompts=None, **kwargs):
        if prompts is None:
            prompts = [PageTitlePrompt.name]
        super().__init__(*args, prompts=prompts, **kwargs)

    class BoundPanel(AIPanelMixin.BoundPanel, TitleFieldPanel.BoundPanel):  # type: ignore
        pass


class AIDescriptionFieldPanel(AIFieldPanel):
    def __init__(self, *args, prompts=None, **kwargs):
        if prompts is None:
            prompts = [PageDescriptionPrompt.name]
        super().__init__(*args, prompts=prompts, **kwargs)


class AIChooserPanelMixin(Panel):
    def __init__(
        self,
        *args,
        suggest_limit: int = 3,
        chunk_size: int | None = None,
        vector_index: "str | VectorIndex",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.suggest_limit = suggest_limit
        self.chunk_size = chunk_size
        if isinstance(vector_index, str):
            self.vector_index = vector_index
        else:
            self.vector_index = vector_index.index_id

    def clone_kwargs(self):
        return {
            **super().clone_kwargs(),
            "vector_index": self.vector_index,
            "suggest_limit": self.suggest_limit,
            "chunk_size": self.chunk_size,
        }

    @classproperty
    def BASE_ATTRS(cls):
        base = super().BASE_ATTRS
        controllers = [base.get("data-controller", ""), "wai-chooser-panel"]
        actions = [
            base.get("data-action", ""),
            "w-formset:removed->wai-chooser-panel#updateControlStates",
            "w-formset:added->wai-chooser-panel#updateControlStates",
            "w-formset:ready->wai-chooser-panel#updateControlStates",
        ]
        return {
            **base,
            "data-controller": " ".join(controllers).strip(),
            "data-action": " ".join(actions).strip(),
        }

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtail_ai/panels/chooser_panel.html"

        @classproperty
        def original_template_name(cls):
            return super().template_name

        @property
        def attrs(self):
            attrs = super().attrs
            attrs["data-wai-chooser-panel-relation-name-value"] = (
                self.panel.relation_name
            )
            attrs["data-wai-chooser-panel-instance-pk-value"] = (
                self.instance.pk if self.instance else None
            )
            attrs["data-wai-chooser-panel-limit-value"] = self.panel.suggest_limit
            attrs["data-wai-chooser-panel-vector-index-value"] = self.panel.vector_index
            if self.panel.chunk_size:
                attrs["data-wai-chooser-panel-chunk-size-value"] = self.panel.chunk_size
            return attrs

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context=parent_context) or {}
            context["original_template_name"] = self.original_template_name
            return context

        @cached_property
        def media(self):  # type: ignore
            return super().media + forms.Media(
                js=[versioned_static("wagtail_ai/chooser_panel.js")],
                css={"all": [versioned_static("wagtail_ai/chooser_panel.css")]},
            )


class AIMultipleChooserPanel(AIChooserPanelMixin, MultipleChooserPanel):
    class BoundPanel(AIChooserPanelMixin.BoundPanel, MultipleChooserPanel.BoundPanel):  # type: ignore
        pass
