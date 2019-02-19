import os, random, time, string
from django.core.validators import FileExtensionValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.deconstruct import deconstructible

from uuid import uuid4

from apiNomad.models import User


class Video(models.Model):
    class Meta:
        verbose_name_plural = 'Videos'
        ordering = ('is_created',)

    @deconstructible
    class PathAndRename(object):
        def __init__(self, sub_path):
            self.path = sub_path

        def __call__(self, instance, filename):
            ext = filename.split('.')[-1]
            f_name = '-'.join(filename.replace(ext, '').split())
            rand_strings = ''.join(
                random.choice(string.ascii_lowercase + string.digits) for i in range(7))
            filename = '{}_{}{}.{}'.format(f_name, rand_strings, uuid4().hex, ext)

            path_video = os.path.join(self.path, filename)

            return path_video

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Owners",
    )
    duration = models.FloatField(
        verbose_name='duration',
        blank=False,
        null=False,
    )
    width = models.PositiveIntegerField(
        verbose_name='width',
        blank=False,
        null=False,
    )
    height = models.PositiveIntegerField(
        verbose_name='height',
        blank=False,
        null=False,
    )
    size = models.PositiveIntegerField(
        verbose_name='size',
        blank=False,
        null=False,
    )
    title = models.CharField(
        verbose_name="Title",
        max_length=255,
        blank=True,
        null=True
    )
    file = models.FileField(
        upload_to=PathAndRename('uploads/videos/{}'.format(time.strftime("%Y/%m/%d"))),
        blank=False,
        null=False,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm'])]
    )
    description = models.TextField(
        verbose_name="Description",
        blank=True,
        null=True
    )
    is_created = models.DateTimeField(
        verbose_name="Cree le",
        auto_now_add=True,
    )
    is_deleted = models.DateTimeField(
        verbose_name="Date de suppression",
        auto_now_add=True,
    )
    is_actived = models.DateTimeField(
        verbose_name="visible",
        default='1960-01-01',
        blank=False,
        null=False
    )

    def __str__(self):
        return "{} - {}".format(self.title, self.is_created)

    @property
    def is_actived(self):
        return self.is_actived > self.is_created

    # todo
    # @property
    # def is_deleted(self):
    #     return self.is_actived. ==

