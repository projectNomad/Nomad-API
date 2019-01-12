"""APIManageUsers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls import include, url
from django.contrib.auth.views import LoginView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

from .views import (ObtainTemporaryAuthToken, Users, UsersId, UsersActivation,
                    ResetPassword, ChangePassword)

from cuser.forms import AuthenticationForm

urlpatterns = [
    # Admin panel
    url(
        r'^admin/',
        admin.site.urls
    ),
    # Token authentification
    url(
        r'^authentication$',
        ObtainTemporaryAuthToken.as_view(),
        name='token_api'
    ),
    # Forgot password
    url(
        r'^reset_password$',
        ResetPassword.as_view(),
        name='reset_password'
    ),
    url(
        r'^change_password$',
        ChangePassword.as_view(),
        name='change_password'
    ),
    # Users
    url(
        r'^users$',
        Users.as_view(),
        name='users'
    ),
    url(
        r'^users/activate$',
        UsersActivation.as_view(),
        name='users_activation',
    ),
    url(
        r'^users/(?P<pk>\d+)$',
        UsersId.as_view(),
        name='users_id',
    ),
    url(
        r'^profile$',
        UsersId.as_view(),
        kwargs=dict(
            profile=True,
        ),
        name='profile',
    ),
    url(
        r'^accounts/login/$',
        LoginView.as_view(authentication_form=AuthenticationForm),
        name='login'
    ),
    url(
        r'^accounts/',
        include('django.contrib.auth.urls')
    ),
    # Activities
    # url(
    #     r'^activity/',
    #     include('activity.urls', namespace="activity"),
    # ),
    # # Location
    # url(
    #     r'^location/',
    #     include('location.urls', namespace="location"),
    # ),
]

if settings.DEBUG:
    urlpatterns = [
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL, serve, {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True
        }),
    ] + urlpatterns
    urlpatterns += staticfiles_urlpatterns()
