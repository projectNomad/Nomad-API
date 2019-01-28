from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from activity.models import Event, Participation, EventOption
from apiNomad.models import User, Profile
from . import settings


# initialize all groups
def service_save_groupe_users():
    init_tourist_group()
    init_guide_group()


# initialize the guide group
def init_tourist_group():
    # create permission group for guide
    group_tourist, created = Group.objects.get_or_create(
        name=settings.CONSTANT["GROUPS_USER"]["TOURIST_GROUP"]
    )

    init_user_group(settings.CONSTANT["GROUPS_USER"]["TOURIST_GROUP"])

    content_type_event = ContentType.objects.get_for_model(Event)
    all_permissions_event = Permission.objects.filter(
        content_type=content_type_event
    )
    for permission in all_permissions_event:
        if permission.name == 'Can view event':
            group_tourist.permissions.add(permission)

    content_type_participation = \
        ContentType.objects.get_for_model(Participation)
    all_permissions_participation = Permission.objects.filter(
        content_type=content_type_participation
    )
    for permission in all_permissions_participation:
        if permission.name == 'Can add participation':
            group_tourist.permissions.add(permission)


# initialize the guide group
def init_guide_group():
    group_guide, created = Group.objects.get_or_create(
        name=settings.CONSTANT["GROUPS_USER"]["GUIDE_GROUP"]
    )

    init_user_group(settings.CONSTANT["GROUPS_USER"]["GUIDE_GROUP"])

    content_type_event = ContentType.objects.get_for_model(Event)
    all_permissions_event = Permission.objects.filter(
        content_type=content_type_event
    )
    for permission in all_permissions_event:
        group_guide.permissions.add(permission)

    content_type_participation = \
        ContentType.objects.get_for_model(Participation)
    all_permissions_participation = Permission.objects.filter(
        content_type=content_type_participation
    )
    for permission in all_permissions_participation:
        group_guide.permissions.add(permission)

    content_type_eventoption = \
        ContentType.objects.get_for_model(EventOption)
    all_permissions_eventoption = Permission.objects.filter(
        content_type=content_type_eventoption
    )
    for permission in all_permissions_eventoption:
        group_guide.permissions.add(permission)


# define user permission for tourist group and guide group
def init_user_group(group):

    if group == settings.CONSTANT["GROUPS_USER"]["TOURIST_GROUP"]:
        group, created = Group.objects.get_or_create(
            name=settings.CONSTANT["GROUPS_USER"]["TOURIST_GROUP"]
        )
    else:
        group, created = Group.objects.get_or_create(
            name=settings.CONSTANT["GROUPS_USER"]["GUIDE_GROUP"]
        )

    content_type_user = ContentType.objects.get_for_model(User)
    all_permissions_user = Permission.objects.filter(
        content_type=content_type_user
    )
    for permission in all_permissions_user:
        if permission.name != 'Can view user':
            group.permissions.add(permission)

    content_type_profile = ContentType.objects.get_for_model(Profile)
    all_permissions_profile = Permission.objects.filter(
        content_type=content_type_profile
    )
    for permission in all_permissions_profile:
        if permission.name != 'Can view profile':
            group.permissions.add(permission)
