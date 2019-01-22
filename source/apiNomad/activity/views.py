from rest_framework.response import Response
from rest_framework import status, generics
from django.utils.translation import ugettext_lazy as _
from . import models

from . import serializers
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from .permissions import ParticipationIsManager, EventIsManager


class Event(generics.ListCreateAPIView):
    """
    get:
    Return a list of all the existing events.

    post:
    Create a new events.
    """
    serializer_class = serializers.EventBasicSerializer
    filter_fields = ['participants']

    def get_queryset(self):
        if self.request.user.has_perm('activity.add_event'):
            queryset = models.Event.objects.all()
        else:
            queryset = models.Event.objects.all()

            list_exclude = list()
            for event in queryset:
                if not event.is_active:
                    list_exclude.append(event)

            queryset = queryset.\
                exclude(pk__in=[event.pk for event in list_exclude])

        return queryset

    def post(self, request, *args, **kwargs):

        if self.request.user.has_perm("activity.add_event"):
            return self.create(request, *args, **kwargs)
        content = {
            'detail': _("You are not authorized to create a new event."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class EventId(generics.RetrieveUpdateDestroyAPIView):

    """

    This class holds the methods available to individual event.

    get:
    Return the detail of a specific event.

    patch:
    Update a specific event.

    delete:
    Delete a specific event.

    """
    permission_classes = (
        EventIsManager,
        IsAuthenticated,
        DjangoModelPermissions,
    )

    serializer_class = serializers.EventBasicSerializer

    def get_queryset(self):
        return models.Event.objects.filter()

    def patch(self, request, *args, **kwargs):
        if self.request.user.has_perm('activity.change_event'):
            return self.partial_update(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to update a cell."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if self.request.user.has_perm('activity.delete_event'):
            return self.destroy(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to delete a cell."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class Participations(generics.ListCreateAPIView):

    """

    This view handles the link between User and Activities (participations)

    get:
    Returns a list of the existing Participations. Can be filtered by user with
    ?username=username in the URL.

    post:
    Creates a new Participation.

    """

    serializer_class = serializers.ParticipantionBasicSerializer
    filter_fields = ['event']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Participation.objects.all()
        return models.Participation.objects.filter(user=self.request.user)

    # A user can only create participations for himself
    # This auto-fills the 'user' field of the Participation object.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ParticipationsId(generics.RetrieveUpdateDestroyAPIView):

    """

    This view handles the link between User and Activities (participations)

    get:
    Return the detail of a specific Participation.

    put:
    Fully update a specific Participation.

    patch:
    Partially update a specific Participation.

    delete:
    Delete a specific Participation.

    """

    serializer_class = serializers.ParticipantionBasicSerializer
    permission_classes = (
        IsAuthenticated,
        ParticipationIsManager,
    )

    def get_queryset(self):
        return models.Participation.objects.filter()

    def delete(self, request, *args, **kwargs):
        participation = self.get_object()
        if not participation.event.is_started:
            return self.destroy(request, *args, **kwargs)
        else:
            content = {
                'non_field_errors':
                    _("You can't delete a participation if the associated "
                      "event is already started"),
            }

            return Response(content, status=status.HTTP_403_FORBIDDEN)
