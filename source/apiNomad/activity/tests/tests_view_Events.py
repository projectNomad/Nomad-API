import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.utils import timezone

# from apiNomad.factories import UserFactory, AdminFactory
# from location.models import Address, StateProvince, Country
from apiNomad.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from activity.models import Event, EventOption


class EventsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.user_event_manager = UserFactory()
        self.user_event_manager.set_password('Test123!')
        self.user_event_manager.save()

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

        self.event_option = EventOption.objects.create(
            family=True,
            limit_participant=5
        )

        date_start = timezone.now() + timezone.timedelta(
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
            option=self.event_option,
            date_start=date_start,
            date_end=date_end,
        )

        self.event_with_manager = Event.objects.create(
            guide=self.user_event_manager,
            title='event title2',
            description='description event',
            address=self.address,
            option=self.event_option,
            date_start=date_start,
            date_end=date_end,
        )

        # Decrement date_start for event_2
        date_start = date_start - timezone.timedelta(
            minutes=1,
        )

        self.event_2 = Event.objects.create(
            guide=self.user,
            title='event title3',
            description='description event',
            address=self.address,
            option=self.event_option,
            date_start=date_start,
            date_end=date_end,
        )

    def test_create_new_event_with_permission(self):
        """
        Ensure we can create a new event if we have the permission.
        """
        date_start = timezone.now()
        date_end = date_start + timezone.timedelta(
            minutes=100,
        )

        date_start_str = date_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        date_end_str = date_end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        title = 'event title'
        description = 'description event'

        data = {
            'guide': self.admin.id,
            'title': title,
            'description': description,
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'NS',
                    'name': 'New State',
                },
                'country': {
                    'iso_code': 'NC',
                    'name': 'New Country',
                },
            },
            'option': {
                'family': True,
                'limit_participant': '5',
            },
            'date_start': date_start,
            'date_end': date_end,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('activity:events'),
            data,
            format='json',
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content['date_start'], date_start_str)
        self.assertEqual(content['date_end'], date_end_str)
        self.assertEqual(content['guide']['id'], self.admin.id)
        self.assertEqual(content['title'], title)
        self.assertEqual(content['description'], description)
        self.assertEqual(content['option']['family'], True)
        self.assertEqual(content['option']['limit_participant'], 5)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'date_start', 'date_end', 'guide',
                      'title', 'description', 'address', 'option']

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

    def test_create_new_event_with_event_manager_permission(self):
        """
        Ensure we can create a new event if we have the permission.
        """
        date_start = timezone.now()
        date_end = date_start + timezone.timedelta(
            minutes=100,
        )

        date_start_str = date_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        date_end_str = date_end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        title = 'event title'
        description = 'description event'

        data = {
            'guide': self.admin.id,
            'title': title,
            'description': description,
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'NS',
                    'name': 'New State',
                },
                'country': {
                    'iso_code': 'NC',
                    'name': 'New Country',
                }
            },
            'option': {
                'family': True,
                'limit_participant': '5',
            },
            'date_start': date_start,
            'date_end': date_end,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('activity:events'),
            data,
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content['date_start'], date_start_str)
        self.assertEqual(content['date_end'], date_end_str)
        self.assertEqual(content['title'], title)
        self.assertEqual(content['description'], description)
        self.assertEqual(content['option']['family'], True)
        self.assertEqual(content['option']['limit_participant'], 5)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'date_start', 'date_end', 'guide',
                      'title', 'description', 'address', 'option']

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

    def test_create_new_event_with_date_start_after_date_end(self):
        """
        Ensure we can't create a new event if a date_start after date_end.
        """
        date_end = self.event.date_start + timezone.timedelta(
            minutes=1,
        )
        date_start = self.event.date_end - timezone.timedelta(
            minutes=1,
        )
        title = 'event title'
        description = 'description event'

        data = {
            'guide': self.user.id,
            'title': title,
            'description': description,
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'NS',
                    'name': 'New State',
                },
                'country': {
                    'iso_code': 'NC',
                    'name': 'New Country',
                },
            },
            'option': {
                'family': '1',
                'limit_participant': '5',
            },
            'date_start': date_start,
            'date_end': date_end,
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('activity:events'),
            data,
            format='json',
        )
        content = {
            'non_field_errors': [
                'Start date need to be before the end date.'
            ]
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_event_without_permission(self):
        """
        Ensure we can't create a new event if we don't have the permission.
        """
        date_start = timezone.now()
        date_end = date_start + timezone.timedelta(
            minutes=100,
        )
        title = 'event title'
        description = 'description event'

        data = {
            'title': title,
            'description': description,
            'address': {
                'address_line1': "my address",
                'postal_code': "RAN DOM",
                'city': 'random city',
                'state_province': {
                    'iso_code': 'NS',
                    'name': 'New State',
                },
                'country': {
                    'iso_code': 'NC',
                    'name': 'New Country',
                },
            },
            'option': {
                'family': True,
                'limit_participant': '5',
            },
            'date_start': date_start,
            'date_end': date_end,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('activity:events'),
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        content = {"detail": "You are not authorized to create a new event."}
        self.assertEqual(json.loads(response.content), content)

    def test_list_events_with_permissions(self):
        """
        Ensure we can list all events. (ordered by date_start by default)
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('activity:events'),
            format='json',
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 3)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'date_start', 'date_end', 'guide',
                      'title', 'description', 'address', 'option']

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

        # Make sure the events are ordered in ascending date_start
        self.assertTrue(
            content['results'][0]['date_start'] <=
            content['results'][1]['date_start']
        )
        self.assertTrue(
            content['results'][0]['date_start'] <=
            content['results'][2]['date_start']
        )
        self.assertTrue(
            content['results'][1]['date_start'] <=
            content['results'][2]['date_start']
        )

    def test_list_events_without_permissions(self):
        """
        Ensure we can list only active event (is_active property)
        if we don't have some permissions.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('activity:events'),
            format='json',
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 3)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'date_start', 'date_end', 'guide',
                      'title', 'description', 'address', 'option']

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
