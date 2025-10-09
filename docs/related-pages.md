# Related pages suggestions

Wagtail AI can suggest related pages based on semantic similarity, helping editors discover and link to relevant content in their site. This feature uses vector embeddings and django-ai-core's vector index functionality.

## Overview

The related pages suggestions feature enhances Wagtail's `MultipleChooserPanel` to provide AI-powered content recommendations based on semantic similarity rather than just keyword matching.

## `AIMultipleChooserPanel`

The `AIMultipleChooserPanel` extends Wagtail's `MultipleChooserPanel` to add a "Suggest" button that recommends related pages.


```python
from modelcluster.fields import ParentalKey
from wagtail.models import Page
from wagtail_ai.panels import AIMultipleChooserPanel


class BlogRelatedPage(Orderable, models.Model):
    page = ParentalKey(
        "BlogPage",
        related_name="blog_page_relationship",
        on_delete=models.CASCADE,
    )
    related_page = models.ForeignKey(
        "wagtailcore.Page",
        related_name="page_blog_relationship",
        on_delete=models.CASCADE,
    )
    panels = [FieldPanel("related_page")]


class BlogPage(Page):
    ...

    content_panels = Page.content_panels + [
        AIMultipleChooserPanel(
            "blog_page_relationship",
            chooser_field_name="related_page",
            heading="Related Pages",
            label="Page",
            vector_index="PageIndex",
        ),
    ]
```

## Setting up vector indexing

To use related page suggestions, you need to set up vector indexing with django-ai-core. Here's an example of a `PageIndex` implementation.

```python
# indexes.py
from django_ai_core.contrib.index import (
    CachedEmbeddingTransformer,
    CoreEmbeddingTransformer,
    VectorIndex,
    registry,
)
from django_ai_core.contrib.index.source import ModelSource
from django_ai_core.contrib.index.storage.pgvector import PgVectorProvider
from django_ai_core.llm import LLMService

from .models import BlogPage

llm_embedding_service = LLMService.create(
    provider="openai", model="text-embedding-3-small"
)


@registry.register()
class PageIndex(VectorIndex):
    sources = [
        ModelSource(
            model=BlogPage,
        ),
    ]
    storage_provider = PgVectorProvider()
    embedding_transformer = CachedEmbeddingTransformer(
        base_transformer=CoreEmbeddingTransformer(llm_service=llm_embedding_service),
    )
```

See the [django-ai-core documentation](https://django-ai-core.readthedocs.io) for more details on setting up vector indexes.
