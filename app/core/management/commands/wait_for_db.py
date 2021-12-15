import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Waiting for DB to become available...")
        db_connection = None
        while not db_connection:
            try:
                db_connection = connections["default"]
            except OperationalError:
                self.stdout.write("DB not yet available, waiting 1 second")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("DB available"))
