from django.apps import AppConfig
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate


# @receiver(post_migrate)
# def signal_init_data_database(interactive, **kwargs):
#     group = Group.objects.all()
#     print(group)
#     # setup.service_init_database()

def my_callback(sender, **kwargs):
    group = Group.objects.all()
    print(group)
    pass


class OuziyaConfig(AppConfig):
    name = 'Uziya'
    verbose_name = 'The Uziya app'

    def ready(self):
        post_migrate.connect(my_callback, sender=self)
