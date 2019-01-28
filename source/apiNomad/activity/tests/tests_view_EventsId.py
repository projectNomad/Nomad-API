import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.utils import timezone

from apiNomad.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from activity.models import Event


class EventsIdTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

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
            date_start=date_start,
            date_end=date_end,
        )

    def test_retrieve_event_id_not_exist(self):
        """
        Ensure we can't retrieve an event that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'activity:events_id',
                kwargs={'pk': 999},
            ),
            format='json',
        )

        content = {"detail": "Not found."}

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), content)

    def test_retrieve_event(self):
        """
        Ensure we can retrieve an event.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'activity:events_id',
                kwargs={'pk': self.event.id},
            )
        )

        result = json.loads(response.content)
        self.assertEqual(result['id'], self.event.id)
        self.assertEqual(result['title'], self.event.title)
        self.assertEqual(result['description'], self.event.description)
        self.assertEqual(
            result['date_start'],
            self.event.date_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        self.assertEqual(
            result['date_end'],
            self.event.date_end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        self.assertEqual(result['guide']['id'], self.event.guide.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event_with_permission(self):
        """
        Ensure we can update a specific event.
        """

        title = 'new title event'
        description = 'new description event'
        data_post = {
            "title": title,
            "description": description,
        }

        self.admin.is_superuser = True
        self.admin.save()

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'activity:events_id',
                kwargs={'pk': self.event.id},
            ),
            data_post,
            format='json',
        )

        result = json.loads(response.content)

        self.assertEqual(result['id'], self.event.id)
        self.assertEqual(
            result['title'],
            title,
        )
        self.assertEqual(
            result['description'],
            description,
        )
        self.assertEqual(
            result['date_start'],
            self.event.date_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(
            result['date_end'],
            self.event.date_end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(
            result['guide']['id'],
            self.event.guide.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event_start_date(self):
        """
        Ensure we can partially update a specific event.
        This test works since the associated cycle has nos start_date and
        end_date.
        """

        data_post = {
            "date_start": "2018-09-09T12:00:00Z",
        }

        self.admin.is_superuser = True
        self.admin.save()

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'activity:events_id',
                kwargs={'pk': self.event.id},
            ),
            data_post,
            format='json',
        )

        result = json.loads(response.content)

        self.assertEqual(result['id'], self.event.id)
        self.assertEqual(
            result['date_start'],
            "2018-09-09T12:00:00Z",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event_without_permission(self):
        """
        Ensure we can't update a specific event without permission.
        """
        data_post = {
            "title": 'new update',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'activity:events_id',
                kwargs={'pk': self.event.id},
            ),
            data_post,
            format='json',
        )

        content = {
            'detail': 'You do not have permission to perform this action.'
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_event_that_doesnt_exist(self):
        """
        Ensure we can't update a specific event if it doesn't exist.
        """
        data_post = {
            "title": 'new title',
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'activity:events_id',
                kwargs={'pk': 9999},
            ),
            data_post,
            format='json',
        )

        content = {'detail': "Not found."}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_event_with_permission(self):
        """
        Ensure we can delete a specific event.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'activity:events_id',
                kwargs={'pk': self.event.id},
            ),
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_event_without_permission(self):
        """
        Ensure we can't delete a specific event without permission.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'activity:events_id',
                kwargs={'pk': self.event.id},
            ),
        )

        content = {
            'detail': 'You do not have permission to perform this action.'
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event_that_doesnt_exist(self):
        """
        Ensure we can't delete a specific event if it doesn't exist
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'activity:events_id',
                kwargs={'pk': 9999},
            ),
        )

        content = {'detail': "Not found."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
