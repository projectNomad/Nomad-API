from unittest import mock

from rest_framework.test import APIClient, APITransactionTestCase

from django.db import IntegrityError
from django.utils import timezone

from apiNomad.factories import UserFactory, AdminFactory
from location.models import Address, StateProvince, Country
from activity.models import Event, Participation


class ParticipationTests(APITransactionTestCase):

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

        event_date_start = timezone.now()
        self.event = Event.objects.create(
            guide=self.user,
            title='event title',
            description='description event',
            address=self.address,
            date_start=event_date_start,
            date_end=event_date_start + timezone.timedelta(minutes=100),
        )

        self.participation = Participation.objects.create(
            user=self.user,
            event=self.event,
        )

        self.event_2 = Event.objects.create(
            guide=self.user,
            title='event title',
            description='description event',
            address=self.address,
            date_start=event_date_start,
            date_end=event_date_start + timezone.timedelta(minutes=100),
        )

        self.participation_presence = Participation.objects.create(
            user=self.admin,
            event=self.event_2,
        )

    def test_create_participation(self):
        """
        Ensure we can create a new participation with just required arguments
        """

        date_created = timezone.now()

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = date_created
            participation = Participation.objects.create(
                user=self.admin,
                event=self.event,
            )
        self.assertEqual(participation.date_created, date_created)
        self.assertEqual(participation.user.id, self.admin.id)
        self.assertEqual(participation.event.id, self.event.id)

    def test_create_participation_missing_event(self):
        """
        Ensure we can't create a new participation without required event
        """
        date_created = timezone.now()

        self.assertRaises(
            IntegrityError,
            Participation.objects.create,
            date_created=date_created,
            user=self.user,
        )

    def test_create_participation_missing_user(self):
        """
        Ensure we can't create a new participation without required user
        """
        date_created = timezone.now()

        self.assertRaises(
            IntegrityError,
            Participation.objects.create,
            date_created=date_created,
            event=self.event,
        )

    def test_date_start_property(self):
        """
        Check date_start property
        """

        self.assertEqual(
            self.event.date_start,
            self.participation.event.date_start
        )

    def test_date_end_property(self):
        """
        Check date_end property
        """

        self.assertEqual(
            self.event.date_end,
            self.participation.event.date_end
        )

    def test_name(self):
        self.assertIsNot(self.participation.__str__, None)
