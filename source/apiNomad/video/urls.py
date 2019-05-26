from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from . import signals

app_name = 'video'

urlpatterns = format_suffix_patterns(
    [
        # Video
        url(
            r'^$',
            views.Video.as_view(),
            name='videos',
        ),
        url(
            r'^(?P<pk>\d+)$',
            views.VideoId.as_view(),
            name='videos_id',
        ),
        url(
            r'^activate/(?P<pk>\d+)$',
            views.ActivateOrNot.as_view(),
            name='activateOrNot_id',
        ),
        # Genres
        url(
            r'^genres$',
            views.Genre.as_view(),
            name='genres',
        ),
        url(
            r'^genres/delete$',
            views.VideoGenreId.as_view(),
            name='genresVideos_id',
        ),
        # Images
        url(
            r'^images$',
            views.Image.as_view(),
            name='image',
        ),
    ]
)
