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
    class BoundPanel(AIPanelMixin.BoundPanel, TitleFieldPanel.BoundPanel):  # type: ignore
        pass


class AISuggestionsPanel(MultipleChooserPanel):
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
        controllers = [base.get("data-controller", ""), "wai-suggestions"]
        return {
            **base,
            "data-controller": " ".join(controllers).strip(),
        }

    class BoundPanel(MultipleChooserPanel.BoundPanel):
        template_name = "wagtail_ai/panels/suggestions_panel.html"

        @property
        def attrs(self):
            attrs = super().attrs
            attrs["data-wai-suggestions-relation-name-value"] = self.panel.relation_name
            attrs["data-wai-suggestions-instance-pk-value"] = (
                self.instance.pk if self.instance else None
            )
            attrs["data-wai-suggestions-limit-value"] = self.panel.suggest_limit
            attrs["data-wai-suggestions-vector-index-value"] = self.panel.vector_index
            attrs["data-wai-suggestions-chunk-size-value"] = self.panel.chunk_size
            return attrs

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context=parent_context) or {}
            context["parent_prefix"] = self.prefix.replace("content-child-", "content-")
            return context

        @cached_property
        def media(self):  # type: ignore
            return super().media + forms.Media(
                js=[versioned_static("wagtail_ai/suggestions_panel.js")],
                css={"all": [versioned_static("wagtail_ai/suggestions_panel.css")]},
            )
