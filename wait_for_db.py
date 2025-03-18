# backend/wait_for_db.py
import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Esperando por la base de datos...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Base de datos no disponible, esperando 1 segundo...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('¡Base de datos disponible!'))