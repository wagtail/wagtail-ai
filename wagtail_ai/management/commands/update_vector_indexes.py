from django.core.management.base import BaseCommand

from wagtail_ai.vector_backends import get_vector_backend


class Command(BaseCommand):
    def handle(self, **options):
        self.stdout.write("Rebuilding vector indexes")
        backend = get_vector_backend()
        backend.rebuild_indexes()
