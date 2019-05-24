from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from video.models import Video, Image
# from apiNomad.models import User, Profile
from video.models import Genre
from . import settings


# initialize all groups
# def service_init_database(
#       app_config,
#       verbosity=2,
#       interactive=True,
#       **kwargs):
def service_init_database():
    init_viewer_group()
    init_producer_group()
    init_genre()


# initialize the PRODUCER group
def init_viewer_group():
    # create permission group for PRODUCER
    group_viewer, created = Group.objects.get_or_create(
        name=settings.CONSTANT["GROUPS_USER"]["VIEWER"]
    )

    init_user_group(settings.CONSTANT["GROUPS_USER"]["VIEWER"])

    content_type_video = ContentType.objects.get_for_model(Video)
    all_permissions_event = Permission.objects.filter(
        content_type=content_type_video
    )
    for permission in all_permissions_event:
        if permission.name == 'Can view video':
            group_viewer.permissions.add(permission)


# initialize the PRODUCER group
def init_producer_group():
    group_producer, created = Group.objects.get_or_create(
        name=settings.CONSTANT["GROUPS_USER"]["PRODUCER"]
    )

    # video permissions
    content_type_video = ContentType.objects.get_for_model(Video)
    all_permissions_video = Permission.objects.filter(
        content_type=content_type_video
    )
    for permission in all_permissions_video:
        group_producer.permissions.add(permission)

    # image permissions
    content_type_image = ContentType.objects.get_for_model(Image)
    all_permissions_image = Permission.objects.filter(
        content_type=content_type_image
    )
    for permission in all_permissions_image:
        group_producer.permissions.add(permission)


# define user permission for viewer group and producer group
def init_user_group(group):

    if group == settings.CONSTANT["GROUPS_USER"]["PRODUCER"]:
        group, created = Group.objects.get_or_create(
            name=settings.CONSTANT["GROUPS_USER"]["PRODUCER"]
        )

    # content_type_user = ContentType.objects.get_for_model(User)
    # all_permissions_user = Permission.objects.filter(
    #     content_type=content_type_user
    # )
    # for permission in all_permissions_user:
    #     if permission.name != 'Can view user':
    #         group.permissions.add(permission)
    #
    # content_type_profile = ContentType.objects.get_for_model(Profile)
    # all_permissions_profile = Permission.objects.filter(
    #     content_type=content_type_profile
    # )
    # for permission in all_permissions_profile:
    #     if permission.name != 'Can view profile':
    #         group.permissions.add(permission)


# start init movie genre
def init_genre():
    genres = [
        Genre(
            label='Action',
            description="Action films usually include high energy, "
                        "big-budget physical stunts and chases, possibly "
                        "with rescues, battles, fights, escapes, "
                        "destructive crises (floods, explosions, natural "
                        "disasters, fires, etc.), non-stop motion, "
                        "spectacular rhythm and pacing, and adventurous, "
                        "often two-dimensional 'good-guy' heroes "
                        "(or recently, heroines) battling 'bad guys' - "
                        "all designed for pure audience escapism. "
                        "Includes the James Bond 'fantasy' "
                        "spy/espionage series, martial arts films, "
                        "video-game films, so-called 'blaxploitation' "
                        "films, and some superhero films. (See "
                        "Superheroes on Film: History.) A major "
                        "sub-genre is the disaster film. See also Greatest "
                        "Disaster and Crowd Film Scenes and Greatest "
                        "Classic Chase Scenes in Films."
        ),
        Genre(
            label='Adventure',
            description="Adventure films are usually exciting stories, "
                        "with new experiences or exotic locales, very "
                        "similar to or often paired with the action "
                        "film genre. They can include traditional "
                        "swashbucklers or pirate films, serialized films, "
                        "and historical spectacles (similar to "
                        "the epics film genre), searches or "
                        "expeditions for lost continents, 'jungle' "
                        "and 'desert' epics, treasure hunts, disaster "
                        "films, or searches for the unknown."
        ),
        Genre(
            label='Comedy',
            description="Comedies are light-hearted plots consistently and "
                        "deliberately designed to amuse and provoke laughter "
                        "(with one-liners, jokes, etc.) by exaggerating the "
                        "situation, the language, action, relationships and "
                        "characters. This section describes various forms of "
                        "comedy through cinematic history, including "
                        "slapstick, screwball, spoofs and parodies, romantic "
                        "comedies, black comedy (dark satirical comedy), "
                        "and more. See this site's Funniest Film Moments and "
                        "Scenes collection - illustrated, also Premiere "
                        "Magazine's 50 Greatest Comedies of All Time, and "
                        "WGA's 101 Funniest Screenplays of All Time."
        ),
        Genre(
            label='Crime',
            description="Crime (gangster) films are developed around the "
                        "sinister actions of criminals or mobsters, "
                        "particularly bankrobbers, underworld figures, or "
                        "ruthless hoodlums who operate outside the law, "
                        "stealing and murdering their way through life. "
                        "The criminals or gangsters are often counteracted "
                        "by a detective-protagonist with a who-dun-it plot. "
                        "Hard-boiled detective films reached their peak "
                        "during the 40s and 50s (classic film noir), "
                        "although have continued to the present day. "
                        "Therefore, crime and gangster films are often "
                        "categorized as film noir or detective-mystery "
                        "films, and sometimes as courtroom/crime legal "
                        "thrillers - because of underlying similarities "
                        "between these cinematic forms. This category also "
                        "includes various 'serial killer' films."
        ),
        Genre(
            label='Drama',
            description="Dramas are serious, plot-driven presentations, "
                        "portraying realistic characters, settings, life "
                        "situations, and stories involving intense character "
                        "development and interaction. Usually, they are not "
                        "focused on special-effects, comedy, or action, "
                        "Dramatic films are probably the largest film "
                        "genre, with many subsets. See also melodramas, "
                        "epics (historical dramas), courtroom dramas, or "
                        "romantic genres. Dramatic biographical films "
                        "(or 'biopics') are a major sub-genre, as are 'adult' "
                        "films (with mature subject content)."
        ),
        Genre(
            label='Horror',
            description="Horror films are designed to frighten and to invoke "
                        "our hidden worst fears, often in a terrifying, "
                        "shocking finale, while captivating and entertaining "
                        "us at the same time in a cathartic experience. "
                        "Horror films feature a wide range of styles, from "
                        "the earliest silent Nosferatu classic, to today's "
                        "CGI monsters and deranged humans. They are often "
                        "combined with science fiction when the menace "
                        "or monster is related to a corruption of technology, "
                        "or when Earth is threatened by aliens. The fantasy "
                        "and supernatural film genres are not always "
                        "synonymous with the horror genre. There are many "
                        "sub-genres of horror: slasher, splatter, "
                        "psychological, survival, teen terror, 'found "
                        "footage, serial killers, paranormal/occult, "
                        "zombies, Satanic, monsters, Dracula, Frankenstein, "
                        "etc. See this site's Scariest Film Moments and "
                        "Scenes collection - illustrated."
        ),
        Genre(
            label='Musical/dance',
            description="Musical/dance films are cinematic forms that "
                        "emphasize full-scale scores or song and dance "
                        "routines in a significant way (usually with a "
                        "musical or dance performance integrated as part "
                        "of the film narrative), or they are films that "
                        "are centered on combinations of music, dance, "
                        "song or choreography. Major subgenres include "
                        "the musical comedy or the concert film. See this "
                        "site's Greatest Musical Song/Dance Movie Moments "
                        "and Scenes collection - illustrated."
        ),
        Genre(
            label='Science fiction',
            description="Sci-fi films are often quasi-scientific, visionary "
                        "and imaginative - complete with heroes, aliens, "
                        "distant planets, impossible quests, improbable "
                        "settings, fantastic places, great dark and shadowy "
                        "villains, futuristic technology, unknown and "
                        "unknowable forces, and extraordinary monsters "
                        "('things or creatures from space'), either created "
                        "by mad scientists or by nuclear havoc. They are "
                        "sometimes an offshoot of the more mystical fantasy "
                        "films (or superhero films), or they share some "
                        "similarities with action/adventure films. Science "
                        "fiction often expresses the potential of technology "
                        "to destroy humankind and easily overlaps with horror "
                        "films, particularly when technology or alien life "
                        "forms become malevolent, as in the 'Atomic Age' of "
                        "sci-fi films in the 1950s. Science-Fiction "
                        "sub-categories abound: apocalyptic or dystopic, "
                        "space-opera, futuristic noirs, speculative, etc."
        ),
    ]

    for genre in genres:
        result, created = Genre.objects.get_or_create(
            label=genre.label,
            description=genre.description
        )
