import os
import datetime

import pytz
from django.conf import settings
from django.db import Error
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from PIL import Image
from resizeimage import resizeimage

from rest_framework import serializers
from apiNomad.serializers import UserBasicSerializer
from . import models, functions
from .models import Video
from apiNomad.services import service_send_mail


class GenreBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = (
            '__all__'
        )
        read_only_fields = [
            'id',
        ]


class ImageBasicSerializer(serializers.ModelSerializer):
    video = serializers.CharField(
        required=False,
        allow_null=True,
    )

    def resize_images(self, image, thumbnail=False):
        # after resizing, image change a type
        # and the new type don't have a pth attribut'
        path = image.filename
        if thumbnail:
            image = resizeimage.resize_width(
                image,
                settings.CONSTANT['IMAGES']['ORIGIN']
            )
        else:
            image = resizeimage.resize_thumbnail(
                image,
                settings.CONSTANT['IMAGES']['THUMBNAIL']
            )
        image.save(path, 'png')

    def create(self, validated_data):
        poster = models.Image()
        poster_thumbnail = models.Image()
        poster.file = validated_data['file']
        poster.save()

        try:
            # resize image for poster
            image = Image.open(poster.file.path)
            self.resize_images(
                image,
                True
            )

            # do a copy of original image
            pathFile = image.filename.split('/')
            nameFile = 'Thumb_' + pathFile[len(pathFile)-1]
            pathThumbFile = '/' + nameFile
            del pathFile[len(pathFile)-1]
            pathFile = '/'.join(pathFile)
            imageTmp = image.copy()
            imageTmp.save(pathFile + pathThumbFile, 'png')
            # save a copy in database
            pathFile = image.filename.split('/')
            del pathFile[0:9]
            del pathFile[len(pathFile) - 1]
            pathFile = '/'.join(pathFile)
            poster_thumbnail.file = pathFile + pathThumbFile
            poster_thumbnail.save()
            # resize image for thumbnail image
            imageTmp = Image.open(poster_thumbnail.file.path)
            self.resize_images(
                imageTmp
            )

            video = Video.objects.get(id=validated_data['video'])

            if video.id and poster.id:
                old_poster = None
                old_poster_thumbnail = None
                if video.poster:
                    old_poster = video.poster
                if video.poster_thumbnail:
                    old_poster_thumbnail = video.poster_thumbnail

                video.poster = poster
                video.poster_thumbnail = poster_thumbnail
                video.save()

                if old_poster:
                    old_poster.delete()
                if old_poster_thumbnail:
                    old_poster_thumbnail.delete()
        except Error:
            if os.path.exists(poster.file.path):
                functions.deleteEmptyRepository(poster.file.path)

            error = {
                'message': (
                    _("Erreur du serveur. Si cela persiste, "
                      "s'il vous plait veiller contacter "
                      "nos services.")
                )
            }
            raise serializers.ValidationError(error)
        except FileNotFoundError:
            error = {
                'message': (
                    _("Aucun fichiers retrouvés.")
                )
            }
            raise serializers.ValidationError(error)

        return poster

    class Meta:
        model = models.Image
        fields = (
            '__all__'
        )
        read_only_fields = [
            'id',
            'hostPathFile'
        ]


class VideoBasicSerializer(serializers.ModelSerializer):
    owner = UserBasicSerializer(
        read_only=True
    )
    genres = GenreBasicSerializer(
        many=True
    )
    avatar = ImageBasicSerializer(
        read_only=True
    )
    is_active = serializers.SerializerMethodField()
    is_delete = serializers.SerializerMethodField()
    hostPathFile = serializers.SerializerMethodField()
    durationToHMS = serializers.SerializerMethodField()

    def get_is_active(self, obj):
        return obj.is_active

    def get_is_delete(self, obj):
        return obj.is_delete

    def get_hostPathFile(self, obj):
        return obj.hostPathFile

    def get_durationToHMS(self, obj):
        return obj.durationToHMS

    def validate(self, data):
        validated_data = super().validate(data)

        # no validation for second step of video creating
        # no validation for update video
        if 'title' in validated_data.keys():
            return data

        # validation for first step of video creating
        file = validated_data.get(
            'file',
            getattr(self.instance, 'file', None)
        )

        infos_video = functions.getInformationsVideo(file)

        if infos_video['width'] < \
                settings.CONSTANT["VIDEO"]["WIDTH"] \
                and infos_video['height'] < \
                settings.CONSTANT["VIDEO"]["HEIGHT"]:
            error = {
                'message': (
                    _("Dimentions of Video is not valide")
                )
            }
            raise serializers.ValidationError(error)

        return data

    def update(self, instance, validated_data):
        if 'title' in validated_data.keys():
            instance.title = validated_data['title']
        if 'description' in validated_data.keys():
            instance.description = validated_data['description']
        if 'genres' in validated_data.keys():
            for genre in validated_data['genres']:
                genre = models.Genre.objects.filter(
                    label=genre.get("label")
                )[:1].get()
                instance.genres.add(genre)

        instance.save()
        return instance

    def create(self, validated_data):
        infos_video = functions.getInformationsVideo(validated_data["file"])

        video = Video()

        video.owner = self.context['request'].user
        video.file = validated_data['file']
        video.width = infos_video['width']
        video.height = infos_video['height']
        video.size = infos_video['size']
        video.duration = infos_video['duration']
        video.avatar = None

        try:
            video.save()
        except Exception as e:
            if os.path.exists(video.hostPathFile()):
                functions.deleteEmptyRepository(video.hostPathFile())

            error = {
                'message': (
                    _("Erreur du serveur. Si cela persiste, "
                      "s'il vous plait veiller contacter "
                      "nos services.")
                )
            }
            raise serializers.ValidationError(error)

        return video

    class Meta:
        model = models.Video
        fields = (
            '__all__'
        )
        read_only_fields = [
            'id',
            'is_created',
            'duration',
            'size',
            'width',
            'height',
            'owner',
            'hostPathFile',
            'durationToHMS',
            'avatar',
        ]


class VideoGenreIdBasicSerializer(serializers.ModelSerializer):
    genre = GenreBasicSerializer(required=True)
    video = VideoBasicSerializer(required=True)


class ActivateOrNotSerializer(serializers.ModelSerializer):
    owner = UserBasicSerializer(
        read_only=True
    )
    genres = GenreBasicSerializer(
        many=True
    )
    avatar = ImageBasicSerializer(
        read_only=True
    )
    is_active = serializers.SerializerMethodField()
    is_delete = serializers.SerializerMethodField()
    hostPathFile = serializers.SerializerMethodField()
    durationToHMS = serializers.SerializerMethodField()

    def get_is_active(self, obj):
        return obj.is_active

    def get_is_delete(self, obj):
        return obj.is_delete

    def get_hostPathFile(self, obj):
        return obj.hostPathFile

    def get_durationToHMS(self, obj):
        return obj.durationToHMS

    mode = serializers.BooleanField(
        required=False,
    )

    def update(self, instance, validated_data):
        global merge_data
        user = instance.owner
        oldStatus = instance.is_active
        instance.is_actived = datetime.datetime(
            1960, 1, 1, 0, 0, 0, 127325, tzinfo=pytz.UTC
        ) if oldStatus else timezone.now()

        merge_data = {
            'USER_FIRST_NAME': user.first_name,
            'USER_LAST_NAME': user.last_name,
            'VIDEO_ACTIVED': instance.is_active,
            'VIDEO_TITLE': instance.title,
            'VIDEO_URL': instance.hostPathFile,
            'CSS_STYLE': render_to_string('css/actived_mail.css')
        }
        instance.save()

        plain_msg = render_to_string("actived_mail.txt", merge_data)
        msg_html = render_to_string("actived_mail.html", merge_data)
        emails_not_sent = service_send_mail(
            [user.email],
            _("UZIYA - Confirmation d'activation de votre video"),
            plain_msg,
            msg_html
        )

        if len(emails_not_sent) <= 0:
            error = {
                'detail': _("Le status de votre video a été modifié."),
            }
            raise serializers.ValidationError(error)

        return instance

    class Meta:
        model = models.Video
        fields = (
            '__all__'
        )
        read_only_fields = [
            'id',
            'is_created',
            'duration',
            'size',
            'width',
            'height',
            'owner',
            'hostPathFile',
            'durationToHMS',
            'avatar',
            'file',
        ]
