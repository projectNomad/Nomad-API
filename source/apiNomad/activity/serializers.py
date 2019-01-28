from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError

from . import models
from apiNomad.serializers import UserPublicSerializer, UserBasicSerializer
from location.serializers import AddressBasicSerializer
from location.models import Address, StateProvince, Country
from activity.models import EventOption


class ParticipantionBasicSerializer(serializers.ModelSerializer):
    """This class represents the ActivityConstraint model serializer."""

    user = UserBasicSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    def to_representation(self, instance):
        data = dict()
        data['id'] = instance.id
        data['date_created'] = instance.date_created
        data['user'] = UserBasicSerializer(
            instance.user
        ).to_representation(instance.user)
        data['event'] = EventBasicSerializer(
            instance.event
        ).to_representation(instance.event)

        return data

    class Meta:
        model = models.Participation
        fields = (
            'id',
            'user',
            'event',
            'date_created',
        )
        read_only_fields = [
            'id',
            'date_created',
        ]


class EventOptionBasicSerializer(serializers.ModelSerializer):
    """This class represents the option Activity model serializer."""

    option = serializers.DictField()

    class Meta:
        model = models.EventOption
        fields = (
            'id',
            'event',
            'family',
            'limit_participant',
        )


class EventBasicSerializer(serializers.ModelSerializer):
    """This class represents the Activity model serializer."""

    address = serializers.DictField()

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

        event = models.Event()

        event.guide = validated_data['guide']
        event.title = validated_data['title']
        event.description = validated_data['description']
        event.date_start = validated_data['date_start']
        event.date_end = validated_data['date_end']

        address_data = validated_data['address']
        country_data = validated_data['address']['country']
        state_province_data = validated_data['address']['state_province']
        address_data['country'] = country_data['iso_code']
        address_data['state_province'] = state_province_data['iso_code']

        try:
            event_address = Address.objects.get(**address_data)
        except Address.DoesNotExist:
            try:
                event_address = Address()
                event_address.__dict__.update(validated_data['address'])
                event_address.country, created = Country.objects.get_or_create(
                    name__iexact=country_data['name'],
                    iso_code__iexact=country_data['iso_code'],
                    defaults={
                        'iso_code': country_data['iso_code'],
                        'name': country_data['name'],
                    },
                )
            except IntegrityError as err:
                if 'UNIQUE constraint failed' in err.args[0]:
                    error = {
                        'message': (
                            "A Country with that iso_code already exists"
                            if err.args else "Unknown Error"
                        )
                    }
                    raise serializers.ValidationError(error)
            try:
                event_address.state_province, created = (
                    StateProvince.objects.get_or_create(
                        iso_code__iexact=state_province_data['iso_code'],
                        name__iexact=state_province_data['name'],
                        country=event_address.country,
                        defaults={
                            'iso_code': state_province_data['iso_code'],
                            'name': state_province_data['name'],
                        },
                    )
                )
                event_address.save()
            except IntegrityError as err:
                if 'UNIQUE constraint failed' in err.args[0]:
                    error = {
                        'message': (
                            "A StateProvince with that iso_code already exists"
                            if err.args else "Unknown Error"
                        )
                    }
                    raise serializers.ValidationError(error)

        event.address = event_address
        event.save()

        if event.id:
            event_option = EventOption.objects.create(
                event=event,
                family=False,
                limit_participant=0,
            )
            event_option.save()
        else:
            error = {
                'message': (
                    "The options for your event are not "
                    "created because your event was not created"
                )
            }
            raise models.IntegrityError(error)

        return event

    def update(self, instance, validated_data):
        if 'title' in validated_data.keys():
            instance.title = validated_data['title']
        if 'description' in validated_data.keys():
            instance.description = validated_data['description']
        if 'date_start' in validated_data.keys():
            instance.date_start = validated_data['date_start']
        if 'date_end' in validated_data.keys():
            instance.date_end = validated_data['date_end']

        if 'address' in validated_data.keys():
            try:
                address_data = validated_data['address']
                country_data = validated_data['address']['country']
                state_province_data = \
                    validated_data['address']['state_province']

                address_data['country'] = country_data['iso_code']
                address_data['state_province'] = \
                    state_province_data['iso_code']
            except KeyError as err:
                error = {
                    'message': (
                        "Please specify a complete valid address."
                        if err.args else "Unknown Error"
                    )
                }
                raise serializers.ValidationError(error)

            try:
                event_address = Address.objects.get(**address_data)
            except Address.DoesNotExist:
                try:
                    event_address = Address()
                    event_address.__dict__.update(validated_data['address'])
                    event_address.country, created = \
                        Country.objects.get_or_create(
                            name__iexact=country_data['name'],
                            iso_code__iexact=country_data['iso_code'],
                            defaults={
                                'iso_code': country_data['iso_code'],
                                'name': country_data['name'],
                            },
                        )
                except IntegrityError as err:
                    if 'UNIQUE constraint failed' in err.args[0]:
                        error = {
                            'message': (
                                "A Country with that iso_code already exists"
                                if err.args else "Unknown Error"
                            )
                        }
                        raise serializers.ValidationError(error)
                try:
                    event_address.state_province, created = (
                        StateProvince.objects.get_or_create(
                            iso_code__iexact=state_province_data['iso_code'],
                            name__iexact=state_province_data['name'],
                            country=event_address.country,
                            defaults={
                                'iso_code': state_province_data['iso_code'],
                                'name': state_province_data['name'],
                            },
                        )
                    )
                    event_address.save()
                except IntegrityError as err:
                    if 'UNIQUE constraint failed' in err.args[0]:
                        error = {
                            'message': (
                                "A StateProvince with "
                                "that iso_code already exists"
                                if err.args else "Unknown Error"
                            )
                        }
                        raise serializers.ValidationError(error)

            instance.address = event_address

        instance.save()

        return instance

    def to_representation(self, instance):
        data = dict()
        data['id'] = instance.id
        data['guide'] = UserBasicSerializer(
            instance.guide
        ).to_representation(instance.guide)
        data['title'] = instance.title
        data['description'] = instance.description
        data['date_start'] = instance.date_start
        data['date_end'] = instance.date_end
        data['address'] = AddressBasicSerializer(
            instance.address
        ).to_representation(instance.address)

        return data

    class Meta:
        model = models.Event
        fields = (
            'id',
            'guide',
            'address',
            'date_start',
            'date_end',
            'title',
            'description',
            'nb_participants',
        )
        read_only_fields = [
            'id',
            'date_created',
            'nb_participants',
        ]
