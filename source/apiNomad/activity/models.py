from django.db import models, IntegrityError
from django.utils import timezone
from django.conf import settings

from location.models import Address
from apiNomad.models import User


class Event(models.Model):

    class Meta:
        verbose_name_plural = 'Events'
        ordering = ('date_start',)

    guide = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Guides",
    )
    address = models.ForeignKey(
        Address,
        blank=False,
        on_delete=models.CASCADE,
    )
    participants = models.ManyToManyField(
        User,
        verbose_name="Participants",
        related_name="participants",
        blank=True,
        null=True,
        through='Participation',
    )
    nb_participants = models.PositiveIntegerField(
        verbose_name="Number of participants",
        default=0,
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
    date_start = models.DateTimeField(
        verbose_name="Start date",
        null=True
    )
    date_end = models.DateTimeField(
        verbose_name="End date",
        null=True
    )

    def clean(self):
        if not self.date_start:
            raise IntegrityError("The event start date cannot be empty.")
        if not self.date_end:
            raise IntegrityError("The event end date cannot be empty.")
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                error = "The start date needs to be older than end date."
                raise IntegrityError(error)
        if not self.title:
            raise IntegrityError("The event title cannot be empty.")
        if not self.description:
            raise IntegrityError("The event description cannot be empty.")

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

    @property
    def nb_participants(self):
        return self.participants.count()


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
        User,
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
