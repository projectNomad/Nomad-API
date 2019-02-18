import os
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from .models import Video


@receiver(pre_delete, sender=Video)
def ma_fonction_de_suppression(sender, instance, **kwargs):
    """
    deletes the video file before its data is deleted from the database

    :param sender: reference model on which the function should be called
    :param instance: data deleted
    :param kwargs:
    :return:
    """

    path = settings.MEDIA_ROOT +'/'+ instance.file.name

    if os.path.exists(path):
        os.remove(path)
    else:
        raise FileNotFoundError(_('Fichier non retrouvé'))

    deleteEmptyRepository(path.split('/'))

def deleteEmptyRepository(path):
    """
    delete all empty folders from the media folder

    :param path: path
    :return: nothing
    """

    # in theory there are 4 files after media
    flagPos = 4

    while flagPos >= 0:
        del path[len(path) - 1]
        new_elts_path = '/'.join(path) + '/'

        if os.path.exists(new_elts_path):
            try:
                os.rmdir(new_elts_path)
            except:
                break
                # raise Exception(_('le dossier n\'est pas vide'))
        else:
            break
            # raise FileNotFoundError(_('dossier non retrouvé'))

        flagPos -= 1
