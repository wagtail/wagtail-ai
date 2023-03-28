from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from wagtail_ai.index import EmbeddingField, ModelVectorIndex, VectorIndexed, registry


class ExamplePage(VectorIndexed, Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    embedding_fields = [EmbeddingField("title", important=True), EmbeddingField("body")]


class DifferentPage(VectorIndexed, Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    embedding_fields = [EmbeddingField("title", important=True), EmbeddingField("body")]


@registry.register()
class MultiplePageVectorIndex(ModelVectorIndex):
    querysets = [DifferentPage.objects.all()]
