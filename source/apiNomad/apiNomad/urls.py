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
from django.urls import path
from rest_framework.documentation import include_docs_urls
from django.conf.urls import include, url
from django.contrib.auth.views import LoginView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.conf.urls.i18n import i18n_patterns

from .views import (ObtainTemporaryAuthToken, Users, UsersId, UsersActivation,
                    ResetPassword, ChangePassword, UpdatePassword)

from cuser.forms import AuthenticationForm

urlpatterns = [
    # DOCUMENTATION SWAGGER
    path(
        'docs/',
        include_docs_urls(
            title=settings.CONSTANT['ORGANIZATION'] + " API",
            # authentication_classes=[],
            permission_classes=[]
        )
    ),
    # Admin panel
    url(
        r'^admin/',
        admin.site.urls
    )
]

urlpatterns += i18n_patterns(
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
        r'^users/update_password$',
        UpdatePassword.as_view(),
        name='users_update_password',
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
    # Location
    url(
        r'^location/',
        include('location.urls', namespace="location"),
    ),
    # Videos
    url(
        r'^videos/',
        include('video.urls', namespace="video"),
    ),
)

if settings.DEBUG:
    urlpatterns = [
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL, serve, {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True
        }),
    ] + urlpatterns
    urlpatterns += staticfiles_urlpatterns()
