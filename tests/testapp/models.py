from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from wagtail_ai.embedding import EmbeddingField, EmbeddingIndexed


class ExamplePage(EmbeddingIndexed, Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    embedding_fields = [EmbeddingField("title"), EmbeddingField("body")]


class DifferentPage(EmbeddingIndexed, Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    embedding_fields = [EmbeddingField("title"), EmbeddingField("body")]
