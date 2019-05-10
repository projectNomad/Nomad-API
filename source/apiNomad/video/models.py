import datetime
import os
import random
import time
import string

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.deconstruct import deconstructible
from django.conf import settings
import pytz

from uuid import uuid4
from apiNomad.models import User




class Genre(models.Model):
    class Meta:
        verbose_name_plural = 'Genres'
        ordering = ('label',)

    label = models.CharField(
        verbose_name="Title",
        max_length=255,
        blank=False,
    )
    description = models.TextField(
        verbose_name="Description",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.label


@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        f_name = '-'.join(
            filename.replace(
                ext,
                ''
            ).split()
        )
        rand_strings = ''.join(
            random.choice(
                string.ascii_lowercase +
                string.digits) for i in range(7)
        )
        filename = '{}_{}{}.{}'.format(
            f_name,
            rand_strings,
            uuid4().hex,
            ext
        )

        return os.path.join(self.path, filename)


class Video(models.Model):
    class Meta:
        verbose_name_plural = 'Videos'
        ordering = ('is_created',)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Owners",
    )
    duration = models.FloatField(
        verbose_name='duration',
    )
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='videos',
    )
    width = models.PositiveIntegerField(
        verbose_name='width',
    )
    height = models.PositiveIntegerField(
        verbose_name='height',
    )
    size = models.PositiveIntegerField(
        verbose_name='size',
    )
    title = models.CharField(
        verbose_name="Title",
        max_length=255,
        blank=True,
        null=True,
    )
    is_agreed_terms_use = models.BooleanField(
        verbose_name=''
    )

    file = models.FileField(
        upload_to=PathAndRename(
            'uploads/videos/{}'.format(time.strftime("%Y/%m/%d"))
        ),
        blank=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp4', 'webm']
            )
        ]
    )
    description = models.TextField(
        verbose_name="Description",
        blank=True,
        null=True,
    )
    is_created = models.DateTimeField(
        verbose_name="Cree le",
        auto_now_add=True,
    )
    is_deleted = models.DateTimeField(
        verbose_name="Date de suppression",
        default=datetime.datetime(
            1990, 1, 1, 0, 0, 0, 127325, tzinfo=pytz.UTC
        ),
    )
    is_actived = models.DateTimeField(
        verbose_name="visible",
        default=datetime.datetime(
            1990, 1, 1, 0, 0, 0, 127325, tzinfo=pytz.UTC
        ),
    )

    def __str__(self):
        return "{} - {}".format(self.title, self.is_created)

    def secondesToHMS(self, totalSec):
        minutes, sec = divmod(totalSec, 60)
        hours, minutes = divmod(minutes, 60)

        if hours == 0:
            return "%02d:%02d" % (minutes, sec)
        return "%d:%02d:%02d" % (hours, minutes, sec)

    @property
    def is_active(self):
        """
        the video is enable if not deleted and she is actived
        """
        if not self.is_delete:
            return self.is_actived >= self.is_created
        return False

    @property
    def is_delete(self):
        return self.is_deleted >= self.is_created

    @property
    def hostPathFile(self):
        return settings.CONSTANT['SERVER_HOST'] + '/' + \
               settings.MEDIA_URL + '/' + self.file.name

    @property
    def durationToHMS(self):
        return self.secondesToHMS(self.duration)
