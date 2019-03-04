import os
import mock
from django.core.files import File

from rest_framework.test \
    import APIClient, APITransactionTestCase

from apiNomad.factories import UserFactory, AdminFactory
from video.models import Video


class EventTests(APITransactionTestCase):
    TITLE = 'event title'
    DESCRIPTION = 'description event'

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.user2 = UserFactory()
        self.user2.set_password('Test123!')
        self.user2.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

    def test_create_video(self):
        """
        Ensure we can create a new event with just required arguments
        """
        path_video = 'media/upload/2019/01/15/video.mp4'

        video = Video.objects.create(
            owner=self.user,
            title=self.TITLE,
            description=self.DESCRIPTION,
            file=path_video,
            duration=100000,
            width=720,
            height=1080,
            size=20000,
        )

        self.assertEqual(video.title, self.TITLE)
        self.assertEqual(video.description, self.DESCRIPTION)
        self.assertEqual(video.file, path_video)
        self.assertEqual(video.duration, 100000)
        self.assertEqual(video.width, 720)
        self.assertEqual(video.height, 1080)
        self.assertEqual(video.size, 20000)
