from django.contrib import admin

from . import models

admin.site.register(models.Video)
admin.site.register(models.Genre)
admin.site.register(models.Image)
