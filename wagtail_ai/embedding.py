from typing import Iterable, List

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models import Subquery
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .ai_backends import get_ai_backend
from .models import Embedding


EMBEDDING_LENGTH_CHARS = 1000


class EmbeddingService:
    def _get_split_content(self, instance: models.Model) -> List[str]:
        values = []
        for field in instance._meta.model.get_embedding_fields():
            value = field.get_value(instance)
            if isinstance(value, str):
                values.append(value)
            else:
                values.append("\n".join(value))

        text = "\n".join(values)
        splitter = RecursiveCharacterTextSplitter(chunk_size=EMBEDDING_LENGTH_CHARS)
        return splitter.split_text(text)

    def _existing_embeddings_match(
        self, embeddings: Iterable[Embedding], splits: List[str]
    ) -> bool:
        if not embeddings:
            return False

        for embedding in embeddings:
            if embedding.content in splits:
                splits.remove(embedding.content)

        if not splits:
            return True

        return False

    @transaction.atomic
    def embeddings_for_instance(
        self,
        instance: models.Model,
    ) -> Iterable[Embedding]:
        splits = self._get_split_content(instance)
        embeddings = Embedding.get_for_instance(instance)

        # If the existing embeddings all match on content, we return them
        # without generating new ones
        if self._existing_embeddings_match(embeddings, splits):
            return embeddings

        # Otherwise we delete all the existing embeddings and get new ones
        Embedding.get_for_instance(instance).delete()

        backend = get_ai_backend()
        generated_embeddings = []
        for split in splits:
            embedding = Embedding.from_instance(instance)
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
