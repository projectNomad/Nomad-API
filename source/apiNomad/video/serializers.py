import os
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from rest_framework import serializers
from apiNomad.serializers import UserBasicSerializer
from . import models, functions
from .models import Video, Image


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
    hostPathFile = serializers.SerializerMethodField()
    video = serializers.CharField(
        required=False,
        allow_null=True,
    )

    def validate(self, data):
        validated_data = super().validate(data)

        if 'file' in validated_data.keys() and 'video' in validated_data.keys():
            return data
        error = {
            'message': (
                _("Data required")
            )
        }
        raise serializers.ValidationError(error)

    def get_hostPathFile(self, obj):
        return obj.hostPathFile

    def create(self, validated_data):
        poster = models.Image()
        poster.file = validated_data['file']

        try:
            poster.save()
            video = Video.objects.get(id=validated_data['video'])

            if video.id and poster.id:
                old_poster = None
                if video.avatar:
                    old_poster = video.avatar

                video.avatar = poster
                video.save()

                if old_poster:
                    old_poster.delete()
        except Exception as e:
            if os.path.exists(poster.hostPathFile()):
                functions.deleteEmptyRepository(poster.hostPathFile())

            error = {
                'message': (
                    _("Erreur du serveur. Si cela persiste, "
                      "s'il vous plait veiller contacter "
                      "nos services.")
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
    avatar = ImageBasicSerializer()
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
        if 'is_deleted' in validated_data.keys():
            instance.is_deleted = validated_data['is_deleted']
        if 'is_actived' in validated_data.keys():
            instance.is_actived = validated_data['is_actived']
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

        video = models.Video()

        video.owner = self.context['request'].user
        video.file = validated_data['file']
        video.width = infos_video['width']
        video.height = infos_video['height']
        video.size = infos_video['size']
        video.duration = infos_video['duration']

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
        ]


class VideoGenreIdBasicSerializer(serializers.Serializer):
    genre = GenreBasicSerializer(required=True)
    video = VideoBasicSerializer(required=True)
