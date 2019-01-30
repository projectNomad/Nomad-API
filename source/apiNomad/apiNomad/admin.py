from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff'
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

    inlines = (ProfileInline, )


admin.site.register(models.TemporaryToken)
admin.site.register(models.ActionToken)
admin.site.register(models.Profile)
admin.site.register(models.User)
