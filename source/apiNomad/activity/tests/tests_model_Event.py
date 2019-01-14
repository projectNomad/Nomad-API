from rest_framework.test import APIClient, APITransactionTestCase

from django.db import IntegrityError
from django.utils import timezone

# from apiNomad.factories import UserFactory, AdminFactory
from ....apiNomad.apiNomad.factories import UserFactory, AdminFactory
from ....apiNomad.location.models import Address, StateProvince, Country
# from location.models import Address, StateProvince, Country
from ..models import Event, Participation


class EventTests(APITransactionTestCase):
    TITLE = 'event title'
    DESCRIPTION = 'description event'

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

    def test_create_event(self):
        """
        Ensure we can create a new event with just required arguments
        """
        date_start = timezone.now()
        end_date = date_start + timezone.timedelta(
            minutes=100
        )

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )
        print(event.guide)
        self.assertEqual(event.date_start, date_start)
        self.assertEqual(event.end_date, end_date)
        self.assertEqual(event.title, self.TITLE)
        self.assertEqual(event.description, self.DESCRIPTION)
        self.assertEqual(event.limit_participant, 0)

    def test_create_event_missing_date_start(self):
        """
        Ensure we can't create a new event without required date_start
        """
        date_start = timezone.now()
        end_date = date_start + timezone.timedelta(
            minutes=100
        )

        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            end_date=end_date,
        )

    def test_create_event_missing_date_end(self):
        """
        Ensure we can't create a new event without required end_date
        """
        date_start = timezone.now()

        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
        )

    def test_is_expired_property_true(self):
        """
        Ensure we have True if the event is expired
        """
        date_start = timezone.now()
        end_date = date_start

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

        self.assertEqual(event.is_expired, True)

    def test_is_expired_property_false(self):
        """
        Ensure we have False if the event is not expired
        """
        date_start = timezone.now()
        end_date = date_start + timezone.timedelta(
            minutes=100
        )

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

        self.assertEqual(event.is_expired, False)

    def test_is_active_property_true(self):
        """
        Ensure we have True if the event is active
        """
        date_start = timezone.now()
        end_date = date_start + timezone.timedelta(
            minutes=100,
        )

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

        self.assertEqual(event.is_active, True)

    def test_is_active_property_false(self):
        """
        Ensure we have False if the event is not active
        """
        date_start = timezone.now()
        end_date = date_start

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

        self.assertEqual(event.is_active, False)

    def test_create_event_with_end_date_older_than_date_start(self):
        """
        Ensure we can't create a new event with an end_date older
        than the date_start.
        """
        # Here we have an end_date older than the date_start
        end_date = timezone.now()
        date_start = end_date + timezone.timedelta(
            minutes=100,
        )

        self.assertRaises(
            IntegrityError,
            Event.objects.create,
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

    def test_participants_property(self):
        """
        Ensure we get the correct number of volunteers that are signed up
        """
        date_start = timezone.now()
        end_date = date_start

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

        Participation.objects.create(
            user=self.user,
            event=event,
        )

        Participation.objects.create(
            user=self.user2,
            event=event,
        )

        Participation.objects.create(
            user=self.admin,
            event=event,
        )

        self.assertEqual(event.participants, 1)

    def test_nb_volunteers_standby_property(self):
        """
        Ensure we get the correct number of volunteers that are signed up and
        on hold.
        """
        date_start = timezone.now()
        end_date = date_start

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

        Participation.objects.create(
            user=self.user,
            event=event,
        )

        Participation.objects.create(
            user=self.user2,
            event=event,
        )

        self.assertEqual(event.participants, 2)

    def test_is_started_property_false(self):
        """
        Ensure we have False if the event is not started
        """
        date_start = timezone.now() + timezone.timedelta(
            minutes=100
        )
        end_date = date_start + timezone.timedelta(
            minutes=100
        )

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

        self.assertEqual(event.is_started, False)

    def test_is_started_property_true(self):
        """
        Ensure we have True if the event is started
        """
        date_start = timezone.now()
        end_date = date_start + timezone.timedelta(
            minutes=100
        )

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

        self.assertEqual(event.is_started, True)

    def test_duration(self):
        """
        Ensure we have True if the event is started
        """
        date_start = timezone.now()
        end_date = date_start + timezone.timedelta(
            minutes=100
        )

        event = Event.objects.create(
            guide=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            date_start=date_start,
            end_date=end_date,
        )

        self.assertEqual(event.duration, end_date - date_start)
