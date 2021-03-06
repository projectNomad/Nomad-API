# Generated by Django 2.1.5 on 2019-03-30 00:19

import django.core.validators
from django.db import migrations, models
import video.models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0004_auto_20190329_0258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='file',
            field=models.FileField(upload_to=video.models.PathAndRename('uploads/videos/2019/03/30'), validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'webm'])]),
        ),
    ]
