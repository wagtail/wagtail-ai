import inspect

from django.core.management.base import BaseCommand

from wagtail_ai.index import get_vector_indexes


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Tells Django to NOT prompt the user for input of any kind.",
        )

    def handle(self, **options):
        interactive = options["interactive"]

        if interactive:
            confirm = input(
                inspect.cleandoc(
                    """
                WARNING:
                You are triggering a Wagtail AI index update.

                Depending on your configured AI backend;
                 * Multiple API calls will be triggered to chargeable services.
                 * Contents from every indexed model will be sent to third-party APIs.

                Are you sure you want to do this?
                Type 'yes' to continue, or 'no' to cancel: """
                )
            )
        else:
            confirm = "yes"

        if confirm == "yes":
            self.stdout.write("Rebuilding vector indexes")
            indexes = get_vector_indexes()
            for _, index in indexes.items():
                index.rebuild_index()
        else:
            self.stdout.write("Index update cancelled")
