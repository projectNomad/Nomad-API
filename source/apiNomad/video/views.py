from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.response import Response

from video.serializers import VideoBasicSerializer
from . import models, serializers
from rest_framework import generics, status
from django.utils.translation import ugettext_lazy as _


class Video(generics.ListCreateAPIView):
    """
    get:
    Return a list of all the existing events.

    post:
    Create a new events.
    """
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)
    serializer_class = serializers.VideoBasicSerializer

    def get_queryset(self):

        if 'params' in self.request.query_params.keys():
            queryset = models.Video.objects.filter(owner=self.request.user)
            list_exclude = list()
            for video in queryset:
                if video.is_delete:
                    list_exclude.append(video)
        else:
            queryset = models.Video.objects.all()
            list_exclude = list()

            if 'is_deleted' in self.request.query_params.keys():
                for video in queryset:
                    if not video.is_delete:
                        list_exclude.append(video)
            elif 'is_actived' in self.request.query_params.keys():
                for video in queryset:
                    if not video.is_active:
                        list_exclude.append(video)

        queryset = queryset.\
            exclude(pk__in=[video.pk for video in list_exclude])

        return queryset

    def post(self, request, *args, **kwargs):

        if self.request.user.has_perm("video.add_video"):
            request.data['owner'] = self.request.user.id

            return self.create(request, *args, **kwargs)

        return Response(
            _("video invalide. \n Revoyer les critères d'acceptation de projet pour "
              "vous assurer que vous êtes en confirmité. Si le probléme persiste, "
              "merci de contacter l'administration"),
            status=status.HTTP_400_BAD_REQUEST
        )

class VideoId(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Return the detail of a specific cycle.

    patch:
    Update a specific cycle.

    delete:
    Delete a specific cycle.
    """

    serializer_class = serializers.VideoBasicSerializer

    def get_queryset(self):
        return models.Video.objects.filter()

    def patch(self, request, *args, **kwargs):

        if 'file' in request.data.keys() or 'owner' in request.data.keys():
            del request.data['file']
            del request.data['owner']

        if self.request.user.has_perm('video.change_video'):
            return self.partial_update(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to update a given video."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
