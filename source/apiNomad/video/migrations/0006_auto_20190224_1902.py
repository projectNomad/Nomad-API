# Generated by Django 2.1.5 on 2019-02-24 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0005_auto_20190224_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='is_deleted',
            field=models.DateTimeField(default='1960-01-01', verbose_name='Date de suppression'),
        ),
    ]
