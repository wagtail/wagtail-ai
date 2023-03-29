# Backends

Wagtail AI supports multiple vector backends for storage and querying of content embeddings.

The vector backend can be configured using the `WAGTAIL_AI_VECTOR_BACKENDS` setting:

```python
WAGTAIL_AI_VECTOR_BACKENDS = {
    "default": {
        "BACKEND": "path.to.backend.class",
        "API_KEY": "abc123",
        "HOST": "https://example.com",
    }
}
```

## Numpy Backend

The Numpy backend is the default backend, but can be configured explicitly with:

```python
WAGTAIL_AI_VECTOR_BACKENDS = {
    "default": {
        "BACKEND": "wagtail_ai.vector_backends.numpy.NumpyBackend",
    }
}
```

It does not need any additional processes to work, but it does require the `numpy` package to be installed.

This backend iterates through each embedding in the database, running similarity checks against content in-memory. This may be useful for small sets of content, but will likely be slow and consume large amounts of memory as the size of indexed content increases. For this reason it is not recommended for production use.

## Qdrant Backend

The [Qdrant](https://qdrant.tech/) backend supports both the cloud and self-hosted versions of the Qdrant vector database.

```python
WAGTAIL_AI_VECTOR_BACKENDS = {
    "default": {
        "BACKEND": "wagtail_ai.vector_backends.qdrant.QdrantBackend",
        "HOST": "https://location/of/qdrant/cluster",
        "API_KEY": "your_qdrant_cloud_api_key",  # Not required for self-hosted installations
    }
}
```
