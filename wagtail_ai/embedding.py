from typing import List

from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import checks
from django.db import models, transaction
from django.db.models import Subquery
from langchain.text_splitter import RecursiveCharacterTextSplitter
from wagtail.search.index import BaseField

from .backends import get_backend
from .models import Embedding


EMBEDDING_LENGTH_CHARS = 1000


class EmbeddingIndexed(models.Model):
    embedding_fields = []
    embeddings = GenericRelation(
        Embedding, content_type_field="base_content_type", for_concrete_model=False
    )

    class Meta:
        abstract = True

    @classmethod
    def get_embedding_fields(cls) -> List["EmbeddingField"]:
        embedding_fields = {}
        for field in cls.embedding_fields:
            embedding_fields[(type(field), field.field_name)] = field

        return list(embedding_fields.values())

    @classmethod
    def check(cls, **kwargs):
        """Extend model checks to include validation of embedding_fields in the
        same way that Wagtail's Indexed class does it."""
        errors = super().check(**kwargs)
        errors.extend(cls._check_embedding_fields(**kwargs))
        return errors

    @classmethod
    def _check_embedding_fields(cls, **kwargs):
        errors = []
        for field in cls.get_embedding_fields():
            message = "{model}.embedding_fields contains non-existent field '{name}'"
            if not cls._has_field(field.field_name):
                errors.append(
                    checks.Warning(
                        message.format(model=cls.__name__, name=field.field_name),
                        obj=cls,
                        id="wagtailai.WA001",
                    )
                )
        return errors


def get_indexed_models():
    return [
        model
        for model in apps.get_models()
        if issubclass(model, EmbeddingIndexed)
        and not model._meta.abstract
        and model.embedding_fields
    ]


class EmbeddingField(BaseField):
    pass


@transaction.atomic
def generate_embeddings_for_instance(instance: models.Model) -> List[Embedding]:
    Embedding.get_for_instance(instance).delete()
    values = []
    for field in instance._meta.model.get_embedding_fields():
        value = field.get_value(instance)
        if isinstance(value, str):
            values.append(value)
        else:
            values.append("\n".join(value))

    text = "\n".join(values)
    splitter = RecursiveCharacterTextSplitter(chunk_size=EMBEDDING_LENGTH_CHARS)
    split_text = splitter.split_text(text)

    backend = get_backend()
    generated_embeddings = []
    for split in split_text:
        embedding = Embedding.build_from_instance(instance)
        embedding.vector = str(backend.get_embedding(split))
        embedding.content = split
        embedding.save()
        generated_embeddings.append(embedding)

    return generated_embeddings


def get_embeddings_for_queryset(queryset):
    try:
        content_type = ContentType.objects.get_for_model(
            queryset.model._meta.get_parent_list()[-1]
        )
    except IndexError:
        content_type = ContentType.objects.get_for_model(queryset.model)

    return Embedding.objects.filter(
        base_content_type=content_type, object_id__in=Subquery(queryset.values("pk"))
    )
