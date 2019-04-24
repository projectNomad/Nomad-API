import coreapi
import coreschema
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, password_validation
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView

from . import serializers, services
from .models import TemporaryToken, ActionToken, User
from django.template.loader import render_to_string


class ObtainTemporaryAuthToken(ObtainAuthToken):
    """
    Enables email/password exchange for expiring token.
    """
    model = TemporaryToken
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="login",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Login",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request):
        """
        Respond to POSTed email/password with token.
        """

        serializer = serializers.AuthCustomTokenSerializer(data=request.data)

        CONFIG = settings.REST_FRAMEWORK_TEMPORARY_TOKENS

        if (serializer.is_valid() or (
                'USE_AUTHENTICATION_BACKENDS'
                in CONFIG and CONFIG['USE_AUTHENTICATION_BACKENDS'])):

            user = None
            try:
                user = serializer.validated_data['user']
            except KeyError:
                if ('email' in request.data and 'password' in request.data):
                    user = authenticate(
                        email=request.data['email'],
                        password=request.data['password']
                    )

                elif ('email' in request.data and
                        'password' in request.data):

                    user = authenticate(
                        email=request.data['email'],
                        password=request.data['password']
                    )

            token = None
            if user:
                token, _created = TemporaryToken.objects.get_or_create(
                    user=user
                )

            if token and token.expired:
                # If the token is expired, generate a new one.
                token.delete()
                expires = timezone.now() + timezone.timedelta(
                    minutes=CONFIG['MINUTES']
                )

                token = TemporaryToken.objects.create(
                    user=user, expires=expires)

            if token:
                data = {'token': token.key}
                return Response(data)
            else:
                error = _("Impossible d'authentifier l'utilisateur.")
                return Response(
                    {'error': error},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Users(generics.ListCreateAPIView):
    """
    get:
    List all users in the system.

    post:
    Create a new user.
    """
    serializer_class = serializers.UserBasicSerializer

    def get_queryset(self):
        return User.objects.all()

    def get(self, request, *args, **kwargs):
        if self.request.user.has_perm('apiNomad.list_user'):
            return self.list(request, *args, **kwargs)

        content = {
            'detail': _("Vous n'êtes pas autorisé à répertorier les utilisateurs."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = ()

        return [permission() for permission in self.permission_classes]

    def get_authenticators(self):
        if self.request.method == 'POST':
            self.authentication_classes = ()
        return [auth() for auth in self.authentication_classes]

    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)
        # get token for user save and send key this token with a mail
        user = User.objects.get(email=request.data["email"])

        if response.status_code == status.HTTP_201_CREATED:
            if settings.CONSTANT['AUTO_ACTIVATE_USER'] is True:
                user.is_active = True
                user.save()

            if settings.CONSTANT['EMAIL_SERVICE'] is True:
                # Send the new token by e-mail to the user
                FRONTEND_SETTINGS = settings.CONSTANT['FRONTEND_INTEGRATION']

                # Get the token of the saved user and send it with an email
                activate_token = ActionToken.objects.get(
                    user=user,
                    type='account_activation',
                ).key

                # data for email activation
                msg_html_css = render_to_string('css/confirm_sign_up.css')
                merge_data = {
                    'ACTIVATION_URL':
                        FRONTEND_SETTINGS['ACTIVATION_URL'].replace(
                            "token",
                            activate_token
                        ),
                    'CSS_STYLE': msg_html_css
                }

                plain_msg = render_to_string("confirm_sign_up.txt", merge_data)
                msg_html = render_to_string("confirm_sign_up.html", merge_data)
                emails_not_sent = services.\
                    service_send_mail([request.data["email"]],
                                      _("Confirmation d\'enregistrement."),
                                      plain_msg, msg_html)

                if len(emails_not_sent) <= 0:
                    content = {
                        'detail': _("Le compte a été créé mais aucun "
                                    "email n'a été envoyé. Si votre compte "
                                    "n'est pas activé, contactez l'administration."),
                    }
                    return Response(content, status=status.HTTP_201_CREATED)

                content = {
                    'detail': _("Le compte a été créé et un email a été "
                                "envoyé avec votre code d'activation."),
                }
                return Response(content, status=status.HTTP_201_CREATED)
            else:
                content = {
                    'detail': _("Le compte a été créé mais aucun email "
                                "n'a été envoyé (service de messagerie "
                                "désactivé). Si votre compte n'est pas "
                                "activé, contactez l\'administration."),
                }
                return Response(content, status=status.HTTP_201_CREATED)

        return response


class UsersId(generics.RetrieveUpdateAPIView):
    """
    get:
    Return the detail of a specific user.
    patch:
    Partially update a user.
    """
    serializer_class = serializers.UserBasicSerializer

    def get_queryset(self):
        return User.objects.filter()

    def get(self, request, *args, **kwargs):
        if 'profile' in self.kwargs.keys():
            self.kwargs['pk'] = self.request.user.id
            return self.retrieve(request, *args, **kwargs)

        elif self.request.user.has_perm('apiNomad.get_user'):
            return self.retrieve(request, *args, **kwargs)

        content = {
            'detail': _("Vous n'êtes pas autorisé à obtenir "
                        "détail d'un utilisateur donné."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, *args, **kwargs):
        if 'profile' in self.kwargs.keys():
            self.kwargs['pk'] = self.request.user.id

            return self.partial_update(request, *args, **kwargs)

        elif self.request.user.has_perm('apiNomad.change_user'):
            return self.partial_update(request, *args, **kwargs)

        content = {
            'detail': _("Vous n'êtes pas autorisé à mettre à jour "
                        "un utilisateur donné."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        content = {
            'non_field_errors': _("Méthode \"PUT\" non alloué.")
        }
        return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UsersActivation(APIView):
    """
    Activate user from an activation token
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.UserBasicSerializer

    def post(self, request):
        """
        Respond to POSTed email/password with token.
        """
        activation_token = request.data.get('activation_token')

        token = ActionToken.objects.filter(
            key=activation_token,
            type='account_activation',
        )

        # There is only one reference, we will set the user active
        if len(token) == 1:
            # We activate the user
            user = token[0].user
            user.is_active = True
            user.save()

            # We delete the token used
            token[0].delete()

            # We return the user
            serializer = serializers.UserBasicSerializer(user)

            return Response(serializer.data)

        # There is no reference to this token
        elif len(token) == 0:
            error = _('"%s" is not a valid activation_token.') % activation_token

            return Response(
                {'non_field_errors': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        # We have multiple token with the same key (impossible)
        else:
            error = _("Le système a un problème, "
                      "s'il vous plaît contactez-nous")
            return Response(
                {'non_field_errors': error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResetPassword(APIView):
    """
    post:
    Create a new token allowing user to change his password.
    """
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):

        if settings.CONSTANT['EMAIL_SERVICE'] is not True:
            # Without email this functionality is not provided
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        # Valid params
        serializer = serializers.ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        text_error_not_email_send = {
                    'detail': _("Votre jeton a été créé mais, aucun email a été "
                                "envoyé. Veuillez contacter l\'administration."),
                }

        # get user from the email given in data
        try:
            user = User.objects.get(email=request.data["email"])
        except Exception:
            content = {
                'non_field_errors': _("Aucun compte avec cet email."),
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # remove old tokens to change password
        tokens = ActionToken.objects.filter(
            type='password_change',
            user=user,
        )

        for token in tokens:
            token.expire()

        # create the new token
        token = ActionToken.objects.create(
            type='password_change',
            user=user,
        )

        try:
            # Send the new token by e-mail to the user
            FRONTEND_SETTINGS = settings.CONSTANT['FRONTEND_INTEGRATION']

            # data for email activation
            msg_html_css = render_to_string('css/reset_password.css')

            merge_data = {
                'FORGOT_URL': FRONTEND_SETTINGS['FORGOT_PASSWORD_URL'].replace(
                    "token",
                    str(token)
                ),
                'CSS_STYLE': msg_html_css
            }
            plain_msg = render_to_string("reset_password.txt", merge_data)
            msg_html = render_to_string("reset_password.html", merge_data)
            response_send_mail = services. \
                service_send_mail([request.data["email"]],
                                  _("Mise à jour du mot de passe."),
                                  plain_msg, msg_html)

            if len(response_send_mail) <= 0:
                return Response(text_error_not_email_send,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_201_CREATED)

        except KeyError:
            return Response(text_error_not_email_send,
                            status=status.HTTP_201_CREATED)


class ChangePassword(APIView):
    """
    post:
    Get a token and a new password and change the password of
    the token's owner.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.UserBasicSerializer

    def post(self, request):
        # Valid params
        serializer = serializers.ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = request.data.get('token')
        new_password = request.data.get('new_password')

        tokens = ActionToken.objects.filter(
            key=token,
            type='password_change',
            expired=False,
        )

        # There is only one reference, we will change the user password
        if len(tokens) == 1:
            user = tokens[0].user
            try:
                password_validation.validate_password(password=new_password)
            except ValidationError as err:
                content = {
                    'non_field_errors': err,
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            # We expire the token used
            tokens[0].expire()

            # We return the user
            serializer = serializers.UserBasicSerializer(user)

            return Response(serializer.data)

        # There is no reference to this token
        elif len(tokens) == 0:
            error = _('%s is not a valid token.') % token

            return Response(
                {'non_field_errors': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        # We have multiple token with the same key (impossible)
        else:
            error = _("Le système a un problème, s'il vous plaît contactez-nous.")
            return Response(
                {'non_field_errors': error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
