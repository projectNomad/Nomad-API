from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apiNomad.serializers import UserBasicSerializer
from . import models, functions

class VideoBasicSerializer(serializers.ModelSerializer):

    def get_queryset(self):
        if self.request.user.has_perm('activity.add_event'):
            queryset = models.Video.objects.all()
        else:
            queryset = models.Video.objects.all()

            list_exclude = list()
            for video in queryset:
                # if not event.is_active:
                list_exclude.append(video)

            queryset = queryset.\
                exclude(pk__in=[video.pk for video in list_exclude])

        return queryset

    def create(self, validated_data):

        infos_video = functions.getInformationsVideo(validated_data["file"])

        if functions.checkVideoUpload(infos_video):

            video = models.Video()

            video.owner = validated_data['owner']
            video.file = validated_data['file']
            video.width = infos_video['width']
            video.height = infos_video['height']
            video.size = infos_video['size']
            video.duration = infos_video['duration']

            video.save()

            return video

        error = {
            'message': (
                _("Video not found")
            )
        }
        raise models.ValidationError(error)

    class Meta:
        model = models.Video
        fields = (
            'id',
            'owner',
            'duration',
            'size',
            'width',
            'height',
            'file',
            'title',
            'description',
            'is_created',
        )
        read_only_fields = [
            'id',
            'date_created',
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
        data['width'] = instance.width
        data['height'] = instance.height
        data['size'] = instance.size
        data['duration'] = instance.duration
        data['file'] = instance.file.name

        return data
