import json

import os.path

from unittest import mock
from django.conf import settings

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.utils import timezone
from django.test.utils import override_settings
from django.contrib.auth.models import Permission

from apiNomad.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Event, Participation
from django.core import mail


@override_settings(EMAIL_BACKEND='anymail.backends.test.EmailBackend')
class ParticipationsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.user2 = UserFactory()
        self.user2.set_password('Test123!')
        self.user2.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.random_country = Country.objects.create(
            name="random country",
            iso_code="RC",
        )
        self.random_state_province = StateProvince.objects.create(
            name="random state",
            iso_code="RS",
            country=self.random_country,
        )
        self.address = Address.objects.create(
            address_line1='random address 1',
            postal_code='RAN DOM',
            city='random city',
            state_province=self.random_state_province,
            country=self.random_country,
        )
        date_start = timezone.now() - timezone.timedelta(
            minutes=100,
        )
        date_end = date_start + timezone.timedelta(
            minutes=50,
        )

        self.event = Event.objects.create(
            guide=self.user,
            title='event title1',
            description='description event',
            address=self.address,
            date_start=date_start,
            date_end=date_end,
        )

        self.event2 = Event.objects.create(
            guide=self.user,
            title='event title2',
            description='description event',
            address=self.address,
            date_start=date_start,
            date_end=date_end,
        )

        self.participation = Participation.objects.create(
            user=self.user,
            event=self.event2,
        )

        self.participation2 = Participation.objects.create(
            user=self.user2,
            event=self.event2,
        )

        self.participation3 = Participation.objects.create(
            user=self.user2,
            event=self.event,
        )

    def test_create_new_participation(self):
        """
        Ensure we can create a new participation.
        """

        data = {
            'event': self.event.id,
            'user': self.user.id,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('activity:participations'),
            data,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content['user']['id'], self.user.id)
        self.assertEqual(content['event']['id'], self.event.id)

        # Check the system doesn't return attributes not expected
        attributes = [
            'id',
            'date_created',
            'user',
            'event',
        ]

        for key in content.keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key),
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes),
        )

    def test_create_duplicate_participation(self):
        """
        Ensure we can't create a duplicated participation.
        """
        subscription_date = timezone.now()

        data = {
            'event': self.event2.id,
            'user': self.user2.id,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('activity:participations'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            'non_field_errors': [
                'The fields event, user must make a unique set.',
            ],
        }
        self.assertEqual(json.loads(response.content), content)

    def test_list_participations(self):
        """
        Ensure we can list all participations.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('activity:participations'),
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 3)

        # Check the system doesn't return attributes not expected
        attributes = [
            'id',
            'user',
            'event',
            'date_created',
        ]

        for key in content['results'][0].keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key),
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes),
        )

    def test_list_participations_filtered_by_email(self):
        """
        Ensure we can filter permissions by username.
        """
        self.client.force_authenticate(user=self.user)

        url = "{0}?participation_id={1}".format(
            reverse('activity:participations'),
            self.participation.id,
        )

        response = self.client.get(
            url,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 1)
        self.assertEqual(content['results'][0]['id'], self.participation.id)

        # Check the system doesn't return attributes not expected
        attributes = [
            'id',
            'user',
            'event',
            'date_created',
        ]

        for key in content['results'][0].keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key),
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes),
        )

    def test_list_participations_filter_by_event(self):
        """
        Ensure we can list participations filtered by event.
        """
        self.client.force_authenticate(user=self.admin)

        url = "{0}?event={1}".format(
            reverse('activity:participations'),
            self.event.id,
        )

        response = self.client.get(
            url,
            format='json',
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 1)
