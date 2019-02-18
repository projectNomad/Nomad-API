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
            r'^update/(?P<pk>\d+)$',
            views.VideoId.as_view(),
            name='videos_id',
        ),
    ]
)