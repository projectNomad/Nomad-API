import json

from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Permission

from apiNomad.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from ..models import Event, Participation


class ParticipationsIdTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.user2 = UserFactory()
        self.user2.set_password('Test123!')
        self.user2.save()

        self.user_cell_manager = UserFactory()
        self.user_cell_manager.set_password('Test123!')

        self.user_cell_manager_no_perms = UserFactory()
        self.user_cell_manager_no_perms.set_password('Test123!')
        self.user_cell_manager_no_perms.save()

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
            minutes=100,
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

        date_created = timezone.now()

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = date_created
            self.participation = Participation.objects.create(
                date_created=date_created,
                user=self.user,
                event=self.event2,
            )

            self.participation2 = Participation.objects.create(
                date_created=date_created,
                user=self.user2,
                event=self.event2,
            )

    def test_retrieve_participation_id_not_exist(self):
        """
        Ensure we can't retrieve a participation that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'activity:participations_id',
                kwargs={'pk': 999},
            ),
            format='json',
        )

        content = {"detail": "Not found."}

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), content)

    def test_retrieve_participation_as_owner(self):
        """
        Ensure we can retrieve a participation as the owner.
        """

        date_created_str = self.participation.date_created.\
            strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = dict(
            id=self.participation.id,
            date_created=date_created_str,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'activity:participations_id',
                kwargs={'pk': self.participation.id},
            )
        )

        content = json.loads(response.content)
        del content['user']
        del content['event']
        self.assertEqual(content, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_participation_basic_serializer(self):
        """
        Ensure we can retrieve a participation.
        Using the BasicSerializer
        """

        date_created_str = self.participation2.date_created.\
            strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        data = dict(
            id=self.participation2.id,
            date_created=date_created_str,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'activity:participations_id',
                kwargs={'pk': self.participation2.id},
            )
        )

        content = json.loads(response.content)

        del content['user']
        del content['event']
        self.assertEqual(content, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_participation_with_permission(self):
        """
        Ensure we can delete a specific participation if the caller owns it.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'activity:participations_id',
                kwargs={'pk': self.participation.id},
            ),
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_participation_but_event_already_started(self):
        """
        Ensure we can't delete a specific participation if
        the event is already started.
        """
        self.client.force_authenticate(user=self.user)

        date_start = timezone.now()
        date_end = date_start + timezone.timedelta(
            minutes=100,
        )

        event = Event.objects.create(
            guide=self.user,
            title='event title1',
            description='description event',
            address=self.address,
            date_start=date_start,
            date_end=date_end,
        )

        participation = Participation.objects.create(
            user=self.user,
            event=event,
        )

        response = self.client.delete(
            reverse(
                'activity:participations_id',
                kwargs={'pk': participation.id},
            ),
        )

        content = {
            'non_field_errors':
                "You can't delete a participation if the "
                "associated event is already started",
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_participation_without_permission(self):
        """
        Ensure we can't delete a specific participation without owning it.
        """

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'activity:participations_id',
                kwargs={'pk': self.participation2.id},
            ),
        )

        content = {
            'detail': "You do not have permission to perform this action.",
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_participation_that_doesnt_exist(self):
        """
        Ensure we can't delete a specific participation if it doesn't exist
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                'activity:participations_id',
                kwargs={'pk': 9999},
            ),
        )

        content = {'detail': "Not found."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
