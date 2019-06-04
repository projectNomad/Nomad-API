from django.conf import settings
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver

from .models import Video, Image
from .functions import deleteEmptyRepository


@receiver(pre_delete, sender=Video)
def signal_file_delete_before_delete_video(sender, instance, **kwargs):
    """
    deletes the video file before its data is deleted from the database

    :param sender: reference model on which the function should be called
    :param instance: data deleted
    :param kwargs:
    :return:
    """
    try:
        deleteEmptyRepository(settings.MEDIA_ROOT + '/' + instance.file.name)
    except FileNotFoundError as e:
        pass


@receiver(post_delete, sender=Video)
def signal_image_delete_after_delete_video(sender, instance, **kwargs):
    """
    deletes the video file before its data is deleted from the database

    :param sender: reference model on which the function should be called
    :param instance: data deleted
    :param kwargs:
    :return:
    """
    try:
        if instance.poster:
            instance.poster.delete()
        if instance.poster_thumbnail:
            instance.poster_thumbnail.delete()
    except FileNotFoundError as e:
        pass


@receiver(pre_delete, sender=Image)
def signal_file_delete_before_delete_image(sender, instance, **kwargs):
    """
    deletes the video file before its data is deleted from the database

    :param sender: reference model on which the function should be called
    :param instance: data deleted
    :param kwargs:
    :return:
    """
    try:
        deleteEmptyRepository(settings.MEDIA_ROOT + '/' + instance.file.name)
    except FileNotFoundError as e:
        pass
