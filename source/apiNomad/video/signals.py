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
        print('je suis dans le signal de video')
        deleteEmptyRepository(settings.MEDIA_ROOT + '/' + instance.file.name)
    except FileNotFoundError as e:
        print('je suis dans le signal ex filenot')
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
        print('je suis dans le signal de video apres delete')
        if instance.avatar:
            instance.avatar.delete()
    except FileNotFoundError as e:
        print('je suis dans le signal ex filenot')
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
        print('je suis dans le signal de image')
        deleteEmptyRepository(settings.MEDIA_ROOT + '/' + instance.file.name)
    except FileNotFoundError as e:
        print('je suis dans le signal de image exp filenot')
        pass
