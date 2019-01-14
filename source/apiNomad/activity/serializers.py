from rest_framework import serializers

from . import models
from django.utils.translation import ugettext_lazy as _
from apiNomad.serializers import UserPublicSerializer, UserBasicSerializer
from apiNomad.location.models import Address


class ParticipantionBasicSerializer(serializers.ModelSerializer):
    """This class represents the ActivityConstraint model serializer."""
    participant = UserBasicSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = models.Participation
        fields = (
            'id',
            'participant',
            'activity',
        )
        read_only_fields = [
            'id',
        ]


class EventBasicSerializer(serializers.ModelSerializer):
    """This class represents the Activity model serializer."""

    def validate(self, data):
        validated_data = super().validate(data)

        date_start = validated_data.get(
            'date_start',
            getattr(self.instance, 'date_start', None)
        )
        date_end = validated_data.get(
            'date_end',
            getattr(self.instance, 'date_end', None)
        )

        if date_start > date_end:
            raise serializers.ValidationError(
                _('Start date need to be before the end date.')
            )

        return data

    def create(self, validated_data):
        address = Address(validated_data['address_line1'],validated_data['city'],
                          validated_data['postal_code'],validated_data['country'],
                          validated_data['state_province'],)
        if validated_data['address_line2']:
            address.address_line2 = validated_data['address_line1']
        address_id = address.save()

        print(address_id)


    class Meta:
        model = models.Event
        fields = (
            'id',
            'guide',
            'date_start',
            'date_end',
            'title',
            'description',
            'youtube_link',
            'family',
            'nb_participant',
            'limit_participant',
            # 'address_line1',
            # 'postal_code',
            # 'city',
            # 'state_province',
            # 'country',
        )
        read_only_fields = [
            'id',
        ]
