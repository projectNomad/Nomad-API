import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.test.utils import override_settings

from apiNomad.models import ActionToken, User
from apiNomad.factories import UserFactory, AdminFactory
from django.core import mail

from anymail.exceptions import AnymailCancelSend
from anymail.signals import pre_send
from django.dispatch import receiver


@override_settings(EMAIL_BACKEND='anymail.backends.test.EmailBackend')
class UsersTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": False,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_new_user_without_service_email(self):
        """
        Ensure we can create a new user if we have the permission even if the
        email service is not activated
        """
        data = {
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'M',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        content = {"detail": "The account was created but no email was sent "
                             "(email service deactivated). If your account is "
                             "not activated, contact the administration."}

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(email="John@mailinator.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertEqual(1, len(activation_token))

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_new_user(self):
        """
        Ensure we can create a new user if we have the permission.
        """
        data = {
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'M',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="John@mailinator.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertEqual(1, len(activation_token))

    def test_create_new_user_without_email(self):
        """
        Ensure we can't create a new user without email
        """
        data = {
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'A'
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {"email": ["This field is required."]}
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_without_password(self):
        """
        Ensure we can't create a new user without password
        """
        data = {
            'email': 'John@mailinator.com',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'A'
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {"password": ["This field is required."]}
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_weak_password(self):
        """
        Ensure we can't create a new user with a weak password
        """
        data = {
            'email': 'John@mailinator.com',
            'password': '19274682736',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'A',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {"password": ['This password is entirely numeric.']}
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_duplicate_email(self):
        """
        Ensure we can't create a new user with an already existing email
        """

        data = {
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'A',
        }

        user = UserFactory()
        user.email = data['email']
        user.save()

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            'email': [
                "An account for the specified email address already exists."
            ]
        }
        self.assertEqual(json.loads(response.content), content)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_user_activation_email(self):
        """
        Ensure that the activation email is sent when user signs up.
        """

        data = {
            'email': 'John@gmail.com',
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'M',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="John@gmail.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertFalse(user.is_active)
        self.assertEqual(1, len(activation_token))

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": False,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_user_activation_not_service_email(self):
        """
        Ensure that the user is notified that no email was sent.
        """
        data = {
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'M',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 0)

        content = {
            'detail': "The account was created but no email "
                      "was sent (email service deactivated). "
                      "If your account is not activated, "
                      "contact the administration.",
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(email="John@mailinator.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertFalse(user.is_active)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_user_activation_email_failure(self):
        """
        Ensure that the user is notified that no email was sent.
        """
        data = {
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'M',
        }

        @receiver(pre_send, weak=False)
        def cancel_pre_send(sender, message, esp_name, **kwargs):
            raise AnymailCancelSend("whoa there")

        self.addCleanup(pre_send.disconnect, receiver=cancel_pre_send)

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 0)

        content = {
            'detail': 'The account was created but no email was sent. '
                      'If your account is not activated, contact the '
                      'administration.',
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(email="John@mailinator.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertFalse(user.is_active)
        self.assertEqual(1, len(activation_token))

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": False,
            "AUTO_ACTIVATE_USER": True,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_create_user_auto_activate(self):
        """
        Ensure that the user is automatically activated.
        """
        data = {
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': 'M',
        }

        response = self.client.post(
            reverse('users'),
            data,
            format='json',
        )

        content = {
            'detail': "The account was created but no email was "
                      "sent (email service deactivated). If your "
                      "account is not activated, contact "
                      "the administration.",
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(email="John@mailinator.com")

        # Test that one message wasn't sent
        self.assertEqual(len(mail.outbox), 0)

        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertTrue(user.is_active)
        self.assertEqual(1, len(activation_token))

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": True,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    def test_list_users(self):
        """
        Ensure we can list all users.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('users'))

        self.assertEqual(json.loads(response.content)['count'], 2)

        first_user = json.loads(response.content)['results'][0]
        self.assertEqual(first_user['id'], self.user.id)

        # Check the system doesn't return attributes not expected
        attributes = [
            'id',
            'email',
            'gender',
            'groups',
            'date_joined',
            'first_name',
            'last_name',
            'is_active',
            'is_superuser',
        ]
        for key in first_user.keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key)
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_without_authenticate(self):
        """
        Ensure we can't list users without authentication.
        """
        response = self.client.get(reverse('users'))

        content = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_without_permissions(self):
        """
        Ensure we can't list users without permissions.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('users'))

        content = {"detail": "You are not authorized to list users."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
