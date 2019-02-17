from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.response import Response
from . import models, serializers
from rest_framework import generics, status
from django.utils.translation import ugettext_lazy as _
from . import functions


class Video(generics.ListAPIView):
    """
    get:
    Return a list of all the existing events.

    post:
    Create a new events.
    """
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)

    def post(self, request, *args, **kwargs):
        if(functions.checkVideoUpload(request.data["file"])):
            file_serializer = serializers.VideoBasicSerializer(data=request.data)

            if file_serializer.is_valid():
                file_serializer.save()
                return Response(
                    file_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    file_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

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
        if self.request.user.has_perm('video.change_video'):
            return self.partial_update(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to update a given video."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
