# Getting Started

Wagtail AI's vector search feature combines integrations with AI 'embedding' APIs and vector databases to give you the tools to perform advanced AI-powered querying across your content.

To do this;

* You set up the models/pages you want to be searchable
* Wagtail AI splits the content of those pages into chunks and fetches embeddings from your configured AI backend.
* It then stores all those embeddings in your configured vector database.
* When querying, your query is converted to an embedding and, using the vector database, is compared to the embeddings for all your existing content.

## What's an Embedding?
An embedding is a big list (vector) of floating point numbers that represent your content in some way. Models like OpenAI's `ada-002` can take content and turn it in to a list of numbers such that content that is similar will have a similar list of numbers.

This way, when you provide a query, we can use the same model to get an embedding of that query and do some maths (cosine similarity) to see what content in your vector database is similar to your query.

## Indexing Your Models/Pages
To index your models, subclass Wagtail AI's `VectorIndexed` model, specifying the fields to be used as part of your embedding:

```python
from django.db import models
from wagtail.models import Page
from wagtail_ai.index import VectorIndexed, EmbeddingField


class MyPage(VectorIndexed, Page):
    body = models.TextField()

    embedding_fields = [EmbeddingField("title"), EmbeddingField("body")]
```

An index will be generated for your model which can be accessed using the `vector_index()` classmethod, e.g.:

```
index = MyPage.vector_index()
```

This index can be used to query the database:

```
index.query("What is the airspeed velocity of an unladen swallow?")

{
    "response": "What do you mean? An African or a European swallow?",
    "sources": [MyPage(1)]
}
```

or to retrieve similar content:

```
page = MyPage.objects.create()
index.similar(page)

[MyPage(2), MyPage(3)]
```


## Indexing across models
If you want to be able to query across multiple models, or on a subset of models, they need to be in a vector index together.

To do this, you can define and register your own `ModelVectorIndex`:

```
from wagtail_ai.index import ModelVectorIndex

class MyModelVectorIndex(ModelVectorIndex):
    querysets = [MyModel.objects.all(), MyOtherModel.objects.filter(name__startswith="AI: ")]
```
