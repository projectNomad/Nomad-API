import json

from django.urls import reverse
from django.core import mail
from django.test.utils import override_settings
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver

from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from anymail.exceptions import AnymailCancelSend
from anymail.signals import pre_send

from apiNomad.factories import UserFactory
from apiNomad.models import ActionToken


@override_settings(EMAIL_BACKEND='anymail.backends.test.EmailBackend')
class ResetPasswordTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.is_active = False
        self.user.save()

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token(self):
        """
        Ensure we can have a new token to change our password
        """
        data = {
            'email': self.user.email,
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 1)

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        self.assertEqual(response.content, b'')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(tokens) == 1)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL1": "fake_url",
            }
        }
    )
    def test_create_new_token_with_call_exception(self):
        """
        Ensure we can not have a new token to change our
        password because exception
        """
        data = {
            'email': self.user.email,
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )
        content = {
            'detail': "Votre jeton a été créé mais, aucun email a été "
                      "envoyé. Veuillez contacter l'administration."
        }

        self.assertEqual(json.loads(response.content), content)
        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(tokens) == 1)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_without_email_param(self):
        """
        Ensure we can't have a new token to change our password without
        give our email in param
        """
        data = dict()

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'email': [_('This field is required.')]
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 0)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_with_an_empty_email_param(self):
        """
        Ensure we can't have a new token to change our password without
        give our email in param
        """
        data = {
            'email': '',
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'email': [_("Ce champ ne peut être vide.")],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 0)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_with_bad_email(self):
        """
        Ensure we can't have a new token to change our password without
        a valid email
        """
        data = {
            'email': 'test',
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'email': [_("Saisissez une adresse email valable.")],
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(len(tokens) == 0)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_when_token_already_exist(self):
        """
        Ensure we can have a new token to change our password
        """
        # We create a token before launch the test
        ActionToken.objects.create(
            user=self.user,
            type='password_change',
        )

        data = {
            'email': self.user.email,
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # Test that one message was sent:
        self.assertEqual(len(mail.outbox), 1)

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
            expired=False,
        )

        self.assertEqual(response.content, b'')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(len(tokens) == 1)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": False,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        }
    )
    def test_create_new_token_without_email_service(self):
        """
        Ensure we can have a new token to change our password
        """
        data = {
            'email': self.user.email,
        }

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # Test that one message was not sent:
        self.assertEqual(len(mail.outbox), 0)

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        self.assertEqual(response.content, b'')
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)
        self.assertTrue(len(tokens) == 0)

    @override_settings(
        CONSTANT={
            "EMAIL_SERVICE": True,
            "FRONTEND_INTEGRATION": {
                "FORGOT_PASSWORD_URL": "fake_url",
            }
        },
    )
    def test_create_new_token_with_failure_email(self):
        """
        Ensure we can nt send email after create new token
        """
        data = {
            'email': self.user.email,
        }

        @receiver(pre_send, weak=False)
        def cancel_pre_send(sender, message, esp_name, **kwargs):
            raise AnymailCancelSend("whoa there")

        self.addCleanup(pre_send.disconnect, receiver=cancel_pre_send)

        response = self.client.post(
            reverse('reset_password'),
            data,
            format='json',
        )

        # Test that one message wasn't sent:
        self.assertEqual(len(mail.outbox), 0)

        # The token has been created
        tokens = ActionToken.objects.filter(
            user=self.user,
            type='password_change',
        )

        content = {
            'detail': _("Votre jeton a été créé mais, "
                        "aucun email a été envoyé. "
                        "Veuillez contacter l'administration.")
        }

        self.assertEqual(json.loads(response.content), content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(tokens) == 1)
