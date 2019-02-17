import os, random, time, string
from django.core.validators import FileExtensionValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

from uuid import uuid4


class Video(models.Model):
    class Meta:
        verbose_name_plural = 'Videos'
        ordering = ('date_created',)

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

    def upload_video_validator(upload_video_obj):
        ext = os.path.splitext(upload_video_obj.name)[1]
        valid_extension = ['.mp4', '.webm']
        if not ext in valid_extension:
            raise ValidationError(
                u'Unsupported file extension, ' + ', '.join(valid_extension) +' only'
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
    date_created = models.DateTimeField(
        verbose_name="Creation date",
        auto_now_add=True,
    )

    def __str__(self):
        return self.title

