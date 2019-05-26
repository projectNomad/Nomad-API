import json
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from apiNomad.factories import AdminFactory, UserFactory
from video.models import Genre


class GenresTests(APITestCase):

    def setUp(self):

        self.client = APIClient()

        self.user = UserFactory()
        self.user.save()

        self.admin = AdminFactory()
        self.admin.save()

        self.user_event_manager = UserFactory()
        self.user_event_manager.save()

        self.genre1 = Genre.objects.create(
            label='genre_1',
            description='description genre_1',
        )

        self.genre2 = Genre.objects.create(
            label='genre_2',
            description='description genre_2',
        )

    def test_list_genres(self):
        """
        Ensure we can list all videos actived.
        (ordered by date_created by default)
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('video:genres'),
            format='json',
        )

        content = json.loads(response.content)
        self.assertEquals(content['count'], 2)
        self.assertEquals(content['results'][0]['id'], 1)
        self.assertEquals(content['results'][1]['id'], 2)
