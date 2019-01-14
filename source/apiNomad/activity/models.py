from django.db import models, IntegrityError
from django.utils import timezone
from django.conf import settings

from location.models import Address


class Event(models.Model):

    class Meta:
        verbose_name_plural = 'Activities'

    guide = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Guides",
    )
    address = models.ForeignKey(
        Address,
        blank=False,
        on_delete=models.CASCADE,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Participants",
        related_name="participants",
        blank=True,
        through='Participation',
    )
    family = models.BooleanField(
        verbose_name="Contraintes activity",
        default=True
    )
    nb_participant = models.PositiveIntegerField(
        verbose_name="Number of participant",
        default=0,
    )
    limit_participant = models.BooleanField(
        verbose_name="Limite de participation",
        default=False
    )
    title = models.CharField(
        verbose_name="Title",
        max_length=100,
    )
    description = models.TextField(
        verbose_name="Description"
    )
    date_created = models.DateTimeField(
        verbose_name="Creation date",
        auto_now_add=True,
    )
    youtube_link = models.URLField(
        verbose_name="Youtube Link",
        blank=True,
        null=True,
    )
    date_start = models.DateTimeField(
        verbose_name="Start date",
    )
    date_end = models.DateTimeField(
        verbose_name="End date",
        blank=True,
        null=True
    )

    def clean(self):
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                error = "The start date needs to be older than end date."
                raise IntegrityError(error)

    def save(self, *args, **kwargs):
        self.clean()
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return '{0}, {1}, {2}, {3} - {4}'.format(
            self.guide,
            self.title,
            str(self.date_created),
            str(self.date_start),
            str(self.date_end),
        )

    @property
    def is_active(self):
        now = timezone.now()
        # Activity is active if it has not ended yet
        # (even if it has not started)
        if self.date_start and self.date_end:
            return self.date_end > now
        # Without date, the activity is active
        return True

    @property
    def is_started(self):
        return self.date_start <= timezone.now()

    @property
    def is_expired(self):
        return self.date_end <= timezone.now()

    @property
    def duration(self):
        return self.date_end - self.date_start


class Participation(models.Model):
    """

    This class represents the Participation model.

    A Participation object is used to join Users and Activity together
    (M2M relationship) and store informations concerning that association.

    """

    class Meta:
        verbose_name_plural = 'Participations'
        unique_together = ('event', 'participant')

    event = models.ForeignKey(
        Event,
        related_name='participation',
        on_delete=models.CASCADE,
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='participation',
        on_delete=models.CASCADE,
    )
    date_created = models.DateTimeField(
        verbose_name="Creation date",
        auto_now_add=True,
    )

    def __str__(self):
        return '{0}, {1}, {2}'.format(
            self.participant,
            self.event,
            str(self.date_created),
        )
