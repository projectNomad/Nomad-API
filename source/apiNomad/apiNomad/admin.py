from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


class CustomUserAdmin(UserAdmin):
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'genders',
        'date_updated',
    ]

    list_filter = [
        'is_staff',
        'is_superuser',
        'is_active',
    ]

    search_fields = [
        'first_name',
        'last_name',
        'email',
    ]


admin.site.register(models.TemporaryToken)
admin.site.register(models.ActionToken)
admin.site.register(models.User)
