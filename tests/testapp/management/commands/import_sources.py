import argparse
import json

from django.core.management.base import BaseCommand, CommandParser
from django.utils.module_loading import import_string
from wagtail.models import Page


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--source_file", nargs=1, type=argparse.FileType("r"))
        parser.add_argument("--model", nargs=1, type=str)
        parser.add_argument("--parent_page_id", nargs=1, type=int)

    def handle(self, *args, **options):
        file = options["source_file"][0]
        model = import_string(options["model"][0])
        parent_page = Page.objects.get(pk=options["parent_page_id"][0])
        sources = json.load(file)
        for item in sources:
            imported = model(title=item["source"], body=item["content"])
            parent_page.add_child(instance=imported)
