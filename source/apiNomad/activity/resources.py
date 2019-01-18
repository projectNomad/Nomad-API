# app/admin.py

from django.utils.translation import ugettext_lazy as _

from import_export import resources
from import_export.fields import Field

from apiVolontaria.models import Profile
from . import models


class ParticipationResource(resources.ModelResource):
    first_name = Field()
    last_name = Field()
    email = Field()

    class Meta:
        model = models.Participation

        fields = (
            'first_name',
            'last_name',
            'email',
            'address',
            'event__date_start',
            'event__date_end',
        )

        export_order = fields

    def get_queryset(self):
        query = self._meta.model.objects.filter()

        if self.date_filter:
            query = query.filter(event__start_date__gte=self.date_filter)

        return query

    def dehydrate_first_name(self, obj):
        return obj.user.first_name

    def dehydrate_last_name(self, obj):
        return obj.user.last_name

    def dehydrate_email(self, obj):
        return obj.user.email

    def dehydrate_address(self, obj):
        return obj.event.address
