from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .setup import service_init_database


class ApiNomadConfig(AppConfig):
    name = 'apiNomad'

    def ready(self):
        post_migrate.connect(service_init_database, sender=self)
