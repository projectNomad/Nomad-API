import os
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apiNomad.serializers import UserBasicSerializer
from . import models, functions


class GenreBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = (
            '__all__'
        )
        read_only_fields = [
            'id',
        ]


class VideoBasicSerializer(serializers.ModelSerializer):
    owner = UserBasicSerializer(
        read_only=True
    )
    genres = GenreBasicSerializer(
        many=True
    )
    is_active = serializers.SerializerMethodField()
    is_delete = serializers.SerializerMethodField()

    def get_is_active(self, obj):
        return obj.is_active

    def get_is_delete(self, obj):
        return obj.is_delete

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
            if os.path.exists(video.is_path_file()):
                functions.deleteEmptyRepository(video.is_path_file())

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
        ]
