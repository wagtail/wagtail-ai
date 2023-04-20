import pytest

from factories import ExamplePageFactory

from wagtail_ai.ai_backends import get_ai_backend
from wagtail_ai.embedding import ModelEmbeddingService
from wagtail_ai.models import Embedding


@pytest.fixture
def embedding_service():
    ai_backend = get_ai_backend()
    embedding_service = ModelEmbeddingService(ai_backend)
    return embedding_service


@pytest.mark.django_db
def test_embeddings_for_instance(embedding_service):
    instance = ExamplePageFactory.create()
    embedding_service.embeddings_for_instance(instance)
    assert Embedding.objects.filter(object_id=instance.pk).count() > 0


@pytest.mark.django_db
def test_embedding_for_same_instance_reuses_old_embeddings(embedding_service):
    instance = ExamplePageFactory.create()
    embeddings1 = embedding_service.embeddings_for_instance(instance)
    embeddings2 = embedding_service.embeddings_for_instance(instance)

    assert list(embeddings1) == list(embeddings2)


@pytest.mark.django_db
def test_embedding_for_changed_instance_generates_new_embeddings(embedding_service):
    instance = ExamplePageFactory.create()
    embeddings1 = embedding_service.embeddings_for_instance(instance)
    instance.body = "New content"
    embeddings2 = embedding_service.embeddings_for_instance(instance)

    assert list(embeddings1) != list(embeddings2)


def test_embedding_for_string(embedding_service):
    test_string = "How could a 5-ounce bird possibly carry a 1-pound coconut?"
    embeddings = embedding_service.embeddings_for_strings([test_string])
    assert len(embeddings) == 1
    assert len(embeddings[0]) > 0


def test_embedding_for_multiple_strings(embedding_service):
    test_strings = [
        "How could a 5-ounce bird possibly carry a 1-pound coconut?",
        "She turned me into a newt.",
    ]
    embeddings = embedding_service.embeddings_for_strings(test_strings)
    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0
