import pytest

from factories import ExamplePageFactory

from wagtail_ai.ai_backends import get_ai_backend
from wagtail_ai.embedding import ModelEmbeddingService
from wagtail_ai.models import Embedding


@pytest.mark.django_db
def test_embeddings_for_instance():
    instance = ExamplePageFactory.create()
    ai_backend = get_ai_backend()
    embedding_service = ModelEmbeddingService(ai_backend)
    embedding_service.embeddings_for_instance(instance)
    assert Embedding.objects.filter(object_id=instance.pk).count() > 0


@pytest.mark.django_db
def test_embedding_for_same_instance_reuses_old_embeddings():
    instance = ExamplePageFactory.create()
    ai_backend = get_ai_backend()
    embedding_service = ModelEmbeddingService(ai_backend)
    embeddings1 = embedding_service.embeddings_for_instance(instance)
    embeddings2 = embedding_service.embeddings_for_instance(instance)

    assert list(embeddings1) == list(embeddings2)


@pytest.mark.django_db
def test_embedding_for_changed_instance_generates_new_embeddings():
    instance = ExamplePageFactory.create()
    ai_backend = get_ai_backend()
    embedding_service = ModelEmbeddingService(ai_backend)
    embeddings1 = embedding_service.embeddings_for_instance(instance)
    instance.body = "New content"
    embeddings2 = embedding_service.embeddings_for_instance(instance)

    assert list(embeddings1) != list(embeddings2)
