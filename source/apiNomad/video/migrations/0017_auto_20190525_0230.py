# Generated by Django 2.1.5 on 2019-05-25 06:30

import datetime
import django.core.validators
from django.db import migrations, models
from django.utils.timezone import utc
import video.models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0016_auto_20190523_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.ImageField(upload_to=video.models.PathAndRename('uploads/images/videos/2019/05/25')),
        ),
        migrations.AlterField(
            model_name='video',
            name='file',
            field=models.FileField(upload_to=video.models.PathAndRename('uploads/videos/2019/05/25'), validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'webm'])]),
        ),
        migrations.AlterField(
            model_name='video',
            name='is_actived',
            field=models.DateTimeField(default=datetime.datetime(1960, 1, 1, 0, 0, 0, 127325, tzinfo=utc), verbose_name='visible'),
        ),
        migrations.AlterField(
            model_name='video',
            name='is_deleted',
            field=models.DateTimeField(default=datetime.datetime(1960, 1, 1, 0, 0, 0, 127325, tzinfo=utc), verbose_name='Date de suppression'),
        ),
    ]
