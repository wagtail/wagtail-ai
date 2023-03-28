import pytest

from factories import ExamplePageFactory
from faker import Faker
from testapp.models import DifferentPage, ExamplePage

from wagtail_ai.index import (
    EmbeddingField,
    VectorIndex,
    get_indexed_models,
    get_vector_indexes,
    registry,
)


fake = Faker()


def test_get_indexed_models():
    indexed_models = get_indexed_models()
    assert indexed_models == [ExamplePage, DifferentPage]


def test_get_vector_indexes():
    indexes = get_vector_indexes()
    expected_class_names = [
        "ExamplePageIndex",
        "DifferentPageIndex",
        "MultiplePageVectorIndex",
    ]
    index_class_names = [index.__class__.__name__ for index in indexes]
    assert set(index_class_names) == set(expected_class_names)


def test_indexed_model_has_vector_index():
    index = ExamplePage.get_vector_index()
    assert index.__class__.__name__ == "ExamplePageIndex"


def test_register_custom_vector_index():
    custom_index = type("MyVectorIndex", (VectorIndex,), {})
    registry.register()(custom_index)
    index_classes = [index.__class__ for index in get_vector_indexes()]
    assert custom_index in index_classes


def test_get_embedding_fields_count(patch_embedding_fields):
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


@pytest.mark.django_db
def test_get_split_content_doesnt_split_when_smaller_than_target_length():
    content_length = 200
    split_length = 205
    body = fake.text(max_nb_chars=content_length)[:content_length]
    instance = ExamplePageFactory.create(body=body)
    splits = instance.get_split_content(split_length=split_length, split_overlap=0)
    assert len(splits) == 1


@pytest.mark.django_db
def test_get_split_content_splits_longer_content():
    content_length = 380
    split_length = 200
    body = fake.text(max_nb_chars=content_length)[:content_length]
    instance = ExamplePageFactory.create(title="a", body=body)
    splits = instance.get_split_content(split_length=split_length, split_overlap=0)
    assert len(splits) == 2


@pytest.mark.django_db
def test_get_split_content_adds_important_field_to_each_split(patch_embedding_fields):
    with patch_embedding_fields(
        ExamplePage, [EmbeddingField("title", important=True), EmbeddingField("body")]
    ):
        body = fake.text(max_nb_chars=200)
        instance = ExamplePageFactory.create(title="Important Title", body=body)
        splits = instance.get_split_content(split_length=50, split_overlap=0)
        assert all(split.startswith(instance.title) for split in splits)
