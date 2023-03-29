# Getting Started

Wagtail AI's vector search feature combines integrations with AI 'embedding' APIs and vector databases to provide tools to perform advanced AI-powered querying across content.

To do this;

* You set up models/pages to be searchable.
* Wagtail AI splits the content of those pages into chunks and fetches embeddings from the configured AI backend.
* It then stores all those embeddings in the configured vector database.
* When querying, the query is converted to an embedding and, using the vector database, is compared to the embeddings for all your existing content.

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

A `ModelVectorIndex` will be generated for your model which can be accessed using the `get_vector_index()` classmethod, e.g.:

```python
index = MyPage.get_vector_index()
```

## Updating indexes

To update all indexes, run the `update_vector_indexes` management command:

```
python manage.py update_vector_indexes
```

To skip the prompt, use the `--noinput` flag.

## Natural language question/answers

The `query` method can be used to ask natural language questions:

```python
index.query("What is the airspeed velocity of an unladen swallow?")

QueryResponse(
    response="What do you mean? An African or a European swallow?", sources=[MyPage(1)]
)
```

Behind the scenes, this:

1. Converts the query in to an embedding
2. Uses the vector backend to find content in the same index that is similar
3. Merges all the matched content in to a single 'context' string
4. Passes the 'context' string along with the original query to the AI backend.

It returns a `QueryResponse` containing the `response` from the AI backend, and `sources`,
a list of objects that were used as context.

## Getting similar content

The `similar` index method can be used to find model instances that are similar to another instance:

```python
index.similar(my_model_instance)

[MyPage(1), MyPage(2)]
```

The passed model instance doesn't have to be in the same index, but it must be a subclass of `VectorIndexed`.

This works by:

1. Generating (or retrieving existing) embeddings for the instance
2. Using the vector database to find matching embeddings
3. Returning the original model instances that were used to generate these matching embeddings

## Searching content

The `search` index method can be used to use natural language to search content in the index.

```python
index.search("Bring me a shrubbery")

[MyPage(1), MyPage(2)]
```

This is similar to querying content, but it only returns content matches without a natural language response.
