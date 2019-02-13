from rest_framework import serializers

from . import models

class VideoBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Video
        fields = (
            'id',
            'file',
            'title',
            'description',
            'date_created',
        )
        read_only_fields = [
            'id',
            'date_created',
        ]
