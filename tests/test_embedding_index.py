from contextlib import contextmanager

import pytest

from factories import DifferentPageFactory, ExamplePageFactory
from testapp.models import DifferentPage, ExamplePage
from wagtail.models import Page

from wagtail_ai.embedding import (
    Embedding,
    EmbeddingField,
    EmbeddingService,
    get_embeddings_for_queryset,
    get_indexed_models,
)


@pytest.fixture(autouse=True)
def use_mock_backend(settings):
    settings.WAGTAIL_AI_BACKENDS = {
        "default": {
            "BACKEND": "mock_backend.MockBackend",
        }
    }


@pytest.fixture
def patch_embedding_fields():
    @contextmanager
    def _patch_embedding_fields(model, new_embedding_fields):
        old_embedding_fields = model.embedding_fields
        model.embedding_fields = new_embedding_fields
        yield
        model.embedding_fields = old_embedding_fields

    return _patch_embedding_fields


def test_embedding_fields_count(patch_embedding_fields):
    with patch_embedding_fields(
        ExamplePage, [EmbeddingField("test"), EmbeddingField("another_test")]
    ):
        assert len(ExamplePage.get_embedding_fields()) == 2


def test_embedding_fields_override(patch_embedding_fields):
    # In the same vein as Wagtail's search index fields, if there are
    # multiple fields of the same type with the same name, only one
    # should be returned
    with patch_embedding_fields(
        ExamplePage, [EmbeddingField("test"), EmbeddingField("test")]
    ):
        assert len(ExamplePage.get_embedding_fields()) == 1


def test_checking_search_fields_errors_with_invalid_field(patch_embedding_fields):
    with patch_embedding_fields(ExamplePage, [EmbeddingField("foo")]):
        errors = ExamplePage.check()
        assert "wagtailai.WA001" in [error.id for error in errors]


def test_get_indexed_models():
    indexed_models = get_indexed_models()
    assert indexed_models == [ExamplePage, DifferentPage]


@pytest.mark.django_db
def test_embeddings_for_instance():
    instance = ExamplePageFactory.create()
    embedding_service = EmbeddingService()
    embedding_service.embeddings_for_instance(instance)
    assert Embedding.objects.filter(object_id=instance.pk).count() > 0


@pytest.mark.django_db
def test_embedding_for_same_instance_reuses_old_embeddings():
    instance = ExamplePageFactory.create()
    embedding_service = EmbeddingService()
    embeddings1 = embedding_service.embeddings_for_instance(instance)
    embeddings2 = embedding_service.embeddings_for_instance(instance)

    assert list(embeddings1) == list(embeddings2)


@pytest.mark.django_db
def test_embedding_for_changed_instance_generates_new_embeddings():
    instance = ExamplePageFactory.create()
    embedding_service = EmbeddingService()
    embeddings1 = embedding_service.embeddings_for_instance(instance)
    instance.body = "New content"
    embeddings2 = embedding_service.embeddings_for_instance(instance)

    assert list(embeddings1) != list(embeddings2)


@pytest.mark.django_db
def test_get_embeddings_for_queryset():
    instance = ExamplePageFactory.create()
    embedding_service = EmbeddingService()
    embeddings = embedding_service.embeddings_for_instance(instance)
    qs = ExamplePage.objects.all()
    assert list(get_embeddings_for_queryset(qs)) == embeddings


@pytest.mark.django_db
def test_get_embeddings_for_queryset_only_returns_embeddings_for_given_model():
    instance = ExamplePageFactory.create()
    instance2 = DifferentPageFactory.create()
    embedding_service = EmbeddingService()
    embeddings = embedding_service.embeddings_for_instance(instance)
    embedding_service.embeddings_for_instance(instance2)
    qs = ExamplePage.objects.all()
    assert list(get_embeddings_for_queryset(qs)) == list(embeddings)


@pytest.mark.django_db
def test_get_embeddings_for_queryset_on_parent_returns_embeddings_for_children():
    instance = ExamplePageFactory.create()
    instance2 = DifferentPageFactory.create()
    embedding_service = EmbeddingService()
    embedding_service.embeddings_for_instance(instance)
    embedding_service.embeddings_for_instance(instance2)
    qs = Page.objects.all()
    assert list(get_embeddings_for_queryset(qs)) == list(Embedding.objects.all())
