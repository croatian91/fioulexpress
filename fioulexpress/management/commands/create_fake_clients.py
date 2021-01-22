from itertools import islice

from django.core.management.base import BaseCommand, CommandError
from fioulexpress.models import Client


class Command(BaseCommand):
    help = "Create fake clients for testing purpose"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int)
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete clients instead of creating",
        )

    def handle(self, *args, **options):
        DEFAULT_COUNT = 10000
        CHUNK_SIZE = 500
        email_prefix = "user.test"
        cnt = 0
        if options["delete"]:
            try:
                print("Deleting clients...")
                Client.objects.filter(email__startswith=email_prefix).delete()
            except Exception as e:
                raise CommandError(e)
            self.stdout.write(self.style.SUCCESS("Successfully deleted test clients"))
            return

        clients_count = options["count"] if options["count"] else DEFAULT_COUNT
        client_objs = (
            Client(email=f"{email_prefix}{i}@test.com") for i in range(clients_count)
        )
        while True:
            batch = list(islice(client_objs, CHUNK_SIZE))
            cnt += CHUNK_SIZE

            if not batch:
                break
            try:
                Client.objects.bulk_create(client_objs, CHUNK_SIZE)
            except Exception as e:
                raise CommandError(e)

            print(f"{cnt} clients created")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {clients_count} clients")
        )
