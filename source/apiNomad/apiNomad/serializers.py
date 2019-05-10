from . import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.models import Group

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import ActionToken, User, Profile


class AuthCustomTokenSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')

        if login and password:
            try:
                user_obj = User.objects.get(email=login)
                if user_obj:
                    login = user_obj.email
            except User.DoesNotExist:
                pass

            user = authenticate(request=self.context.get('request'),
                                email=login, password=password)

            if not user:
                msg = _('Impossible de se connecter avec les '
                        'informations d\'identification fournies.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Doit inclure "login" et "mot de passe".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user

        return attrs


class GroupBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class UserBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_superuser',
            'password',
            'new_password',
            'gender',
            'group',
            'groups',
            'date_joined',
            'is_agreed_terms_use',
        )
        write_only_fields = (
            'password',
            'new_password',
            'is_agreed_terms_use',
        )
        read_only_fields = (
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined',
            'date_updated',
            'date_joined',
            'groups',
        )

    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=_(
                    "An account for the specified email "
                    "address already exists."
                ),
            ),
        ],
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=False, write_only=True)
    date_joined = serializers.DateTimeField(required=False)
    groups = GroupBasicSerializer(many=True, read_only=True)

    gender = serializers.CharField(
        source='profile.gender',
    )
    is_agreed_terms_use = serializers.BooleanField(
        source='profile.is_agreed_terms_use'
    )
    group = serializers.CharField(
        required=False,
        source='group.group',
    )

    def create(self, validated_data):
        try:
            password_validation.validate_password(
                password=validated_data['password']
            )
        except ValidationError as err:
            raise serializers.ValidationError({
                "password": err.messages
                })

        profile_data = None
        group_data = None

        if 'profile' in validated_data.keys():
            profile_data = validated_data.pop('profile')

        if 'group' in validated_data.keys():
            group_data = validated_data.pop('group')

        user = User(**validated_data)

        # Hash the user's password
        user.set_password(validated_data['password'])

        # Put user inactive by default
        user.is_active = False

        user.save()

        # add user group
        if group_data:
            if group_data['group'] == 'producer':
                group = Group.objects.get(
                    name=settings.CONSTANT["GROUPS_USER"]["PRODUCER"]
                )

            user.groups.add(group)

        # create profil user
        if profile_data:
            Profile.objects.create(
                user=user,
                **profile_data
            )

        # Create an ActionToken to activate user in the future
        ActionToken.objects.create(
            user=user,
            type='account_activation',
        )

        return user

    def update(self, instance, validated_data):
        if 'new_password' in validated_data.keys():
            try:
                old_pw = validated_data.pop('password')
            except KeyError:
                raise serializers.ValidationError(
                    _('Champ "mot de passe" manquant. Impossible de '
                      'mettre à jour le mot de passe.')
                )
            new_pw = validated_data.pop('new_password')

            if instance.check_password(old_pw):
                try:
                    password_validation.validate_password(password=new_pw)
                except ValidationError as err:
                    raise serializers.ValidationError({
                        "password": err.messages
                        })
                instance.set_password(new_pw)
            else:
                msg = _("Mauvais mot de passe.")
                raise serializers.ValidationError(msg)

        if 'profile' in validated_data.keys():
            profile_data = validated_data.pop('profile')
            profile = Profile.objects.get_or_create(user=instance)
            profile[0].__dict__.update(profile_data)
            profile[0].save()

        return super(
            UserBasicSerializer,
            self
        ).update(instance, validated_data)


class UserPublicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
        )
        read_only_fields = (
            'id',
            'first_name',
            'last_name',
            'email',
        )


class ResetPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)


class ChangePasswordSerializer(serializers.Serializer):

    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
