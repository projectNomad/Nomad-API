from rest_framework.parsers \
    import MultiPartParser, \
    FormParser, \
    FileUploadParser
from rest_framework.response import Response

from . import models, serializers
from rest_framework import generics, status
from django.utils.translation import ugettext_lazy as _
from apiNomad.setup import service_init_database


class Genre(generics.ListAPIView):
    """
    get:
    Return a list of all the existing genres.
    """
    serializer_class = serializers.GenreBasicSerializer

    def get_queryset(self):
        queryset = models.Genre.objects.all()
        return queryset


class VideoGenreId(generics.UpdateAPIView):

    """

    patch:
    Will delete genre of a video

    """
    serializer_class = serializers.VideoGenreIdBasicSerializer

    def patch(self, request, *args, **kwargs):

        if self.request.user.has_perm("video.uodate_video"):
            if 'genre' in request.data.keys() and \
                    'video' in request.data.keys():
                video_id = request.data['video']
                genre_id = request.data['genre']

                video = models.Video.objects.filter(
                        id=video_id
                    )[:1].get()
                genre = models.Genre.objects.filter(
                        id=genre_id
                    )[:1].get()

                if video and genre:
                    video.genres.remove(genre)
                    return Response(genre.label, status=status.HTTP_200_OK)

        content = {
            'detail': _("You are not authorized to update a given video."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class Video(generics.ListCreateAPIView):
    """
    get:
    Return a list of all the existing genres.

    post:
    Create a new events.
    """
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)
    serializer_class = serializers.VideoBasicSerializer

    def get_queryset(self):
        # service_init_database()

        if 'param' in self.request.query_params.keys():
            queryset = models.Video.objects.filter(
                owner=self.request.user
            )
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
            # request.data['owner'] = self.request.user.id

            return self.create(request, *args, **kwargs)

        return Response(
            _("video invalide. \n Revoyer les critères "
              "d'acceptation de projet pour "
              "vous assurer que vous êtes en confirmité. "
              "Si le probléme persiste, "
              "merci de contacter l'administration"),
            status=status.HTTP_400_BAD_REQUEST
        )


class VideoId(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Return the detail of a specific video.

    patch:
    Update a specific video.

    delete:
    Delete a specific video.
    """

    serializer_class = serializers.VideoBasicSerializer

    def get_queryset(self):
        return models.Video.objects.filter()

    def patch(self, request, *args, **kwargs):

        if 'file' in request.data.keys():
            del request.data['file']
        if 'owner' in request.data.keys():
            del request.data['owner']
        if 'genres' in request.data.keys():
            del request.data['genres']

        if self.request.user.has_perm('video.change_video'):
            return self.partial_update(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to update a given video."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
