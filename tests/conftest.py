from contextlib import contextmanager

import pytest


@pytest.fixture
def patch_embedding_fields():
    @contextmanager
    def _patch_embedding_fields(model, new_embedding_fields):
        old_embedding_fields = model.embedding_fields
        model.embedding_fields = new_embedding_fields
        yield
        model.embedding_fields = old_embedding_fields

    return _patch_embedding_fields


@pytest.fixture(autouse=True)
def use_mock_backend(settings):
    settings.WAGTAIL_AI_BACKENDS = {
        "default": {
            "BACKEND": "mock_backend.MockBackend",
        }
    }
