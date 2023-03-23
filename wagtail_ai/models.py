from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Embedding(models.Model):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="+"
    )
    base_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="+"
    )
    object_id = models.CharField(
        max_length=255,
    )
    content_object = GenericForeignKey(
        "content_type", "object_id", for_concrete_model=False
    )
    vector = models.JSONField()
    content = models.TextField()

    @classmethod
    def _get_base_content_type(cls, model_or_object):
        parents = model_or_object._meta.get_parent_list()
        if parents:
            return ContentType.objects.get_for_model(
                parents[-1], for_concrete_model=False
            )
        else:
            return ContentType.objects.get_for_model(
                model_or_object, for_concrete_model=False
            )

    @classmethod
    def from_instance(cls, instance: models.Model) -> "Embedding":
        content_type = ContentType.objects.get_for_model(instance)
        return Embedding(
            content_type=content_type,
            base_content_type=cls._get_base_content_type(instance),
            object_id=instance.pk,
        )

    @classmethod
    def get_for_instance(cls, instance: models.Model):
        content_type = ContentType.objects.get_for_model(instance)
        return Embedding.objects.filter(
            content_type=content_type, object_id=instance.pk
        )
