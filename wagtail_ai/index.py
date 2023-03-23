from typing import Iterable, List, Type

from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import checks
from django.db import models
from wagtail.search.index import BaseField

from .embedding import EmbeddingService
from .models import Embedding


class VectorIndexRegistry:
    def __init__(self):
        self._registry: List[Type["VectorIndex"]] = []

    def register(self):
        def decorator(cls: Type["VectorIndex"]):
            self._registry.append(cls)
            return cls

        return decorator

    def __iter__(self):
        yield from self._registry


registry = VectorIndexRegistry()


class EmbeddingField(BaseField):
    pass


class VectorIndexed(models.Model):
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

    @classmethod
    def vector_index(cls):
        return type(
            f"{cls.__name__}Index",
            (ModelVectorIndex,),
            {"queryset": cls.objects.all()},
        )


def get_indexed_models():
    return [
        model
        for model in apps.get_models()
        if issubclass(model, VectorIndexed)
        and not model._meta.abstract
        and model.embedding_fields
    ]


class VectorIndex:
    def get_entries(self) -> Iterable[dict]:
        raise NotImplementedError


class ModelVectorIndex(VectorIndex):
    querysets: List[models.QuerySet]

    def get_querysets(self) -> List[models.QuerySet]:
        return self.querysets

    def get_entries(self) -> Iterable[dict]:
        querysets = self.get_querysets()
        for queryset in querysets:
            content_type = ContentType.objects.get_for_model(queryset.model)
            service = EmbeddingService()

            for instance in queryset:
                embeddings = service.embeddings_for_instance(instance)
                metadata = {"content_type": content_type.pk, "object_id": instance.pk}
                for embedding in embeddings:
                    yield {
                        "id": embedding.pk,
                        "vector": embedding.vector,
                        "metadata": metadata,
                    }


def get_vector_indexes() -> List[Type[VectorIndex]]:
    models = get_indexed_models()
    for model in models:
        registry.register()(model.vector_index())

    return list(registry)
