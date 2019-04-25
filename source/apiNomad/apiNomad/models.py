# coding: utf-8

import binascii
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import Group

from rest_framework.authtoken.models import Token
from cuser.models import AbstractCUser
from .managers import ActionTokenManager


ACTIONS_TYPE = [
    ('account_activation', _('Activation de compte')),
    ('password_change', _('Change mot de passe')),
]


class ActionToken(models.Model):
    """
    Class of Token to allow User to do some action.

    Generally, the token is sent by email and serves
    as a "right" to do a specific action.
    """

    key = models.CharField(
        verbose_name="Key",
        max_length=40,
        primary_key=True
    )

    type = models.CharField(
        verbose_name=_('Type d\'action'),
        max_length=100,
        choices=ACTIONS_TYPE,
        null=False,
        blank=False,
        default=None,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='activation_token',
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )

    created = models.DateTimeField(
        verbose_name=_("Date de création"),
        auto_now_add=True
    )

    expires = models.DateTimeField(
        verbose_name=_("Date d\'expiration"),
        blank=True,
    )

    objects = ActionTokenManager()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.expires = timezone.now() + timezone.timedelta(
                minutes=settings.ACTIVATION_TOKENS['MINUTES']
            )
        return super(ActionToken, self).save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a new key"""
        return binascii.hexlify(os.urandom(20)).decode()

    @property
    def expired(self):
        """Returns a boolean indicating token expiration."""
        return self.expires <= timezone.now()

    def expire(self):
        """Expires a token by setting its expiration date to now."""
        self.expires = timezone.now()
        self.save()

    def __str__(self):
        return self.key


class TemporaryToken(Token):
    """Subclass of Token to add an expiration time."""
    expires = models.DateTimeField(
        verbose_name=_("Date d\'expiration"),
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires = timezone.now() + timezone.timedelta(
                minutes=settings.REST_FRAMEWORK_TEMPORARY_TOKENS['MINUTES']
            )

        super(TemporaryToken, self).save(*args, **kwargs)

    @property
    def expired(self):
        """Returns a boolean indicating token expiration."""
        return self.expires <= timezone.now()

    def expire(self):
        """Expires a token by setting its expiration date to now."""
        self.expires = timezone.now()
        self.save()


class User(AbstractCUser):
    date_updated = models.DateTimeField(
        _('Date de modification'),
        default=timezone.now)

    class Meta(AbstractCUser.Meta):
        swappable = 'AUTH_USER_MODEL'


class Profile(models.Model):
    IDONTKNOW = 'A'
    MALE = 'M'
    FEMALE = 'F'

    GENDER_STATUS = (
        (IDONTKNOW, _("Sexe non identifié")),
        (MALE, _('Homme')),
        (FEMALE, _('Femme')),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_STATUS,
        default=IDONTKNOW,
    )

    def save(self, *args, **kwargs):
        self.clean()
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)
