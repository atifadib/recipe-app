"""
Django command to wait for postgresql  docker to come up.
"""
import time
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command for waiting for postgresql"""
    def handle(self, *args, **kwargs):
        """
        Command for waiting to start django app till Postgres
        is ready!
        """
        self.stdout.write('Waiting for database...')
        db_up = False

        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Waiting for databases to Initialize...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database Ready!'))
