from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from apiNomad.factories import AdminFactory, UserFactory
import json


class VideosTests(APITestCase):
    TITLE = 'event title'
    DESCRIPTION = 'description event'

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

        self.user_event_manager = UserFactory()
        self.user_event_manager.set_password('Test123!')
        self.user_event_manager.save()


    # def test_create_new_video_with_permission(self):
    #     path_video = 'media/upload/2019/01/15/video.mp4'
    #
    #     data = {
    #         'file': path_video,
    #     }
    #
    #     self.client.force_authenticate(user=self.admin)
    #
    #     response = self.client.post(
    #         reverse('video:videos'),
    #         data,
    #         # format='json',
    #         content_type='application/x-www-form-urlencoded',
    #     )
    #
    #     content = json.loads(response.content)
