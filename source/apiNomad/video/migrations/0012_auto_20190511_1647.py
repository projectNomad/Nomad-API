# Generated by Django 2.1.5 on 2019-05-11 20:47

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import video.models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0011_remove_video_is_agreed_terms_use'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_thumbnail', models.FileField(upload_to=video.models.PathAndRename('uploads/images/videos/2019/05/11'), validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])),
            ],
            options={
                'verbose_name_plural': 'Images',
            },
        ),
        migrations.AddField(
            model_name='video',
            name='avatar',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Avatar', to='video.Image'),
        ),
    ]