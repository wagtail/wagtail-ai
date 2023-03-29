# Customising

Wagtail AI provides a few ways to customise how your content can be indexed.

## Indexing across models
If you want to be able to query across multiple models, or on a subset of models, they need to be in a vector index together.

To do this, you can define and register your own `ModelVectorIndex`:

```python
from wagtail_ai.index import ModelVectorIndex


class MyModelVectorIndex(ModelVectorIndex):
    querysets = [
        MyModel.objects.all(),
        MyOtherModel.objects.filter(name__startswith="AI: "),
    ]
```

Once populated (with the `update_vector_indexes` management command), this can be queried just like an automatically generated index:

```python
index = MyModelVectorIndex()
index.query("Are you suggesting that coconuts migrate?")
```

## Customising embedding splits

Due to token limitations in AI models, content from indexed models is split up in to chunks, with embeddings generated separately.

By default this is done by merging all `embedding_fields` together and then splitting on new paragraphs, new lines, sentences and words (getting more specific as required) until it fits within a defined split size.

To customise this behaviour, override the `get_split_content` method on a `VectorIndexed` model.

```python
def get_split_content(
    self, *, split_length: int = 800, split_overlap: int = 100
) -> List[str]:
    return ["What? A swallow carrying a coconut?"]
```

It is up to your implementation to respect the requested `split_length` and `split_overlap`.
