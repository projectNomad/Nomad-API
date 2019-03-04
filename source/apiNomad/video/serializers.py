import os
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apiNomad.serializers import UserBasicSerializer
from . import models, functions


class VideoBasicSerializer(serializers.ModelSerializer):
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

        video.owner = validated_data['owner']
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
        ]

    def to_representation(self, instance):
        data = dict()

        data['id'] = instance.id
        data['owner'] = UserBasicSerializer(
            instance.owner
        ).to_representation(instance.owner)
        data['title'] = instance.title
        data['description'] = instance.description
        data['is_created'] = instance.is_created
        data['is_actived'] = instance.is_actived
        data['is_active'] = instance.is_active
        data['is_deleted'] = instance.is_deleted
        data['is_delete'] = instance.is_delete
        data['width'] = instance.width
        data['height'] = instance.height
        data['size'] = instance.size
        data['duration'] = instance.duration
        data['file'] = instance.file.name

        return data
