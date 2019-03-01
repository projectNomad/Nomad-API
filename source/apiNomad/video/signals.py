import os
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from .models import Video
from .functions import deleteEmptyRepository


@receiver(pre_delete, sender=Video)
def ma_fonction_de_suppression(sender, instance, **kwargs):
    """
    deletes the video file before its data is deleted from the database

    :param sender: reference model on which the function should be called
    :param instance: data deleted
    :param kwargs:
    :return:
    """

    deleteEmptyRepository(settings.MEDIA_ROOT +'/'+ instance.file.name)


