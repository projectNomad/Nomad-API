# Generated by Django 2.1.3 on 2019-01-14 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='_state',
            field=models.CharField(default='ooo', max_length=10, verbose_name='Postal Code'),
            preserve_default=False,
        ),
    ]