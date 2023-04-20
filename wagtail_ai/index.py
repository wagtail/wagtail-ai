from dataclasses import dataclass
from typing import Generic, Iterable, List, Type, TypeVar

from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from langchain.text_splitter import RecursiveCharacterTextSplitter
from wagtail.search.index import BaseField

from .ai_backends import get_ai_backend
from .embedding import ModelEmbeddingService
from .models import Embedding
from .vector_backends import SearchResponseDocument, get_vector_backend


EMBEDDING_SPLIT_LENGTH_CHARS = 800
EMBEDDING_SPLIT_OVERLAP_CHARS = 100


class VectorIndexRegistry:
    def __init__(self):
        self._registry: dict[str, Type["VectorIndex"]] = {}

    def register(self):
        def decorator(cls: Type["VectorIndex"]):
            self._registry[cls.__name__] = cls
            return cls

        return decorator

    def __iter__(self):
        return iter(self._registry.items())


registry = VectorIndexRegistry()


class EmbeddingField(BaseField):
    def __init__(self, *args, important=False, **kwargs):
        self.important = important
        super().__init__(*args, **kwargs)


class VectorIndexed(models.Model):
    """Additional behaviour for models that are to be stored in a Vector Index"""

    embedding_fields = []
    embeddings = GenericRelation(
        Embedding, content_type_field="content_type", for_concrete_model=False
    )

    class Meta:
        abstract = True

    @classmethod
    def get_embedding_fields(cls) -> List["EmbeddingField"]:
        embedding_fields = {}
        for field in cls.embedding_fields:
            embedding_fields[(type(field), field.field_name)] = field

        return list(embedding_fields.values())

    def get_split_content(
        self,
        *,
        split_length=EMBEDDING_SPLIT_LENGTH_CHARS,
        split_overlap=EMBEDDING_SPLIT_OVERLAP_CHARS,
    ) -> List[str]:
        """Split the contents of a model instance's `embedding_fields` in to smaller chunks"""
        splittable_content = []
        important_content = []
        embedding_fields = self._meta.model.get_embedding_fields()

        for field in embedding_fields:
            value = field.get_value(self)
            if isinstance(value, str):
                final_value = value
            else:
                final_value = "\n".join(value)

            if field.important:
                important_content.append(final_value)
            else:
                splittable_content.append(final_value)

        text = "\n".join(splittable_content)
        important_text = "\n".join(important_content)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=split_length,
            chunk_overlap=split_overlap,
        )
        return [f"{important_text}\n{text}" for text in splitter.split_text(text)]

    @classmethod
    def check(cls, **kwargs):
        """Extend model checks to include validation of embedding_fields in the
        same way that Wagtail's Indexed class does it."""
        errors = super().check(**kwargs)
        errors.extend(cls._check_embedding_fields(**kwargs))
        return errors

    @classmethod
    def _has_field(cls, name):
        try:
            cls._meta.get_field(name)
            return True
        except FieldDoesNotExist:
            return hasattr(cls, name)

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
    def get_vector_index(cls):
        return type(
            f"{cls.__name__}Index",
            (ModelVectorIndex,),
            {"querysets": [cls.objects.all()]},
        )()


def get_indexed_models():
    """Return all models that are a subclass of VectorIndexed"""
    return [
        model
        for model in apps.get_models()
        if issubclass(model, VectorIndexed) and not model._meta.abstract
    ]


# Represents the type of object returned when querying a VectorIndex
VectorIndexReturnType = TypeVar("VectorIndexReturnType")


@dataclass
class QueryResponse(Generic[VectorIndexReturnType]):
    """Represents a response to the VectorIndex `query` method,
    including a response string and a list of sources that were used to generate the response
    """

    response: str
    sources: List[VectorIndexReturnType]


@dataclass
class Document:
    """Representation of a document that is passed to vector storage backends.

    A document is usually some subset of a model, e.g. some content split out from
    a VectorIndexed model.
    """

    @dataclass
    class Metadata:
        content_type_id: str
        object_id: str
        content: str

    id: str
    vector: List[float]
    metadata: Metadata


class VectorIndex(Generic[VectorIndexReturnType]):
    """Base class for a VectorIndex, representing some set of documents that can be queried"""

    def __init__(self, ai_backend_alias="default", vector_backend_alias="default"):
        super().__init__()

        self.ai_backend = get_ai_backend(ai_backend_alias)
        self.vector_backend = get_vector_backend(alias=vector_backend_alias)
        self.backend_index = self.vector_backend.get_index(self.__class__.__name__)

    def get_documents(self) -> Iterable[Document]:
        raise NotImplementedError

    def query(self, query: str) -> QueryResponse[VectorIndexReturnType]:
        raise NotImplementedError

    def search(self, query: str) -> List[VectorIndexReturnType]:
        raise NotImplementedError

    def build_index(self):
        self.vector_backend.delete_index(self.__class__.__name__)
        index = self.vector_backend.create_index(
            self.__class__.__name__, vector_size=self.ai_backend.embedding_dimensions
        )
        index.upsert(documents=self.get_documents())


class ModelVectorIndex(VectorIndex[models.Model]):
    """A VectorIndex which stores embeddings in an Embedding model"""

    querysets: List[models.QuerySet]

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.embedding_service = ModelEmbeddingService(self.ai_backend)

    def get_querysets(self) -> List[models.QuerySet]:
        return self.querysets

    def build_index(self):
        """Before building an index, generate Embedding objects for everything in
        this index"""
        querysets = self.get_querysets()

        for queryset in querysets:
            for instance in queryset:
                self.embedding_service.embeddings_for_instance(instance)

        return super().build_index()

    def get_documents(self) -> Iterable[Document]:
        querysets = self.get_querysets()

        for queryset in querysets:
            for instance in queryset.prefetch_related("embeddings"):
                for embedding in instance.embeddings.all():
                    assert isinstance(embedding, Embedding)
                    yield Document(
                        id=embedding.pk,
                        vector=embedding.vector,
                        metadata=Document.Metadata(
                            content_type_id=embedding.content_type.pk,
                            object_id=embedding.object_id,
                            content=embedding.content,
                        ),
                    )

    def _get_instance_from_response_document(
        self, response_document: SearchResponseDocument
    ) -> models.Model:
        ct = ContentType.objects.get_for_id(
            response_document.metadata["content_type_id"]
        )
        return ct.get_object_for_this_type(pk=response_document.metadata["object_id"])

    def query(self, query):
        query_embedding = self.embedding_service.embeddings_for_strings([query])[0]
        similar_documents = self.backend_index.similarity_search(query_embedding)
        sources = [
            self._get_instance_from_response_document(doc) for doc in similar_documents
        ]
        merged_context = "\n".join(doc.metadata["content"] for doc in similar_documents)
        user_messages = [
            "You are a helpful assistant. Use the following context to answer the question. Don't mention the context in your answer.",
            merged_context,
            query,
        ]
        response = self.ai_backend.prompt(
            system_messages=[], user_messages=user_messages
        )
        return QueryResponse(response=response, sources=sources)

    def similar(self, instance: "VectorIndexed") -> List[models.Model]:
        instance_embeddings = self.embedding_service.embeddings_for_instance(instance)
        similar_documents = []
        for embedding in instance_embeddings:
            similar_documents += self.backend_index.similarity_search(embedding)

        return list(
            {
                self._get_instance_from_response_document(doc)
                for doc in set(similar_documents)
            }
        )

    def search(self, query: str, *, limit: int = 5):
        query_embedding = self.embedding_service.embeddings_for_strings([query])[0]
        similar_documents = self.backend_index.similarity_search(
            query_embedding, limit=limit
        )
        return list(
            {
                self._get_instance_from_response_document(doc)
                for doc in similar_documents
            }
        )


def get_vector_indexes() -> dict[str, VectorIndex]:
    models = get_indexed_models()
    for model in models:
        registry.register()(model.get_vector_index().__class__)

    return {name: index() for name, index in registry}
