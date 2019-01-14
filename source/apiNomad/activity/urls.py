from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'activity'

urlpatterns = format_suffix_patterns(
    [
        # Events
        url(
            r'^events$',
            views.Event.as_view(),
            name='events',
        ),
        url(
            r'^events/(?P<pk>\d+)$',
            views.EventId.as_view(),
            name='events_id',
        ),
        # Participations
        url(
            r'^participations$',
            views.Participations.as_view(),
            name='participations',
        ),
        url(
            r'^participations/(?P<pk>\d+)$',
            views.ParticipationsId.as_view(),
            name='participations_id',
        ),
    ]
)
