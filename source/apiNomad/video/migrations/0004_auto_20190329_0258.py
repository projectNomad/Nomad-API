# Generated by Django 2.1.5 on 2019-03-29 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0003_auto_20190329_0244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='genres',
            field=models.ManyToManyField(related_name='videos', to='video.Genre'),
        ),
    ]
