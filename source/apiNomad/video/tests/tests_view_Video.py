import json
from unittest import mock
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apiNomad.factories import AdminFactory, UserFactory
from video.models import Video, Genre


class VideosTests(APITestCase):

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

        subscription_date = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = subscription_date

            self.video_admin = Video.objects.create(
                title='video test 1',
                description='description test 1',
                owner=self.admin,
                duration=1415.081748,
                width=settings.CONSTANT["VIDEO"]["WIDTH"],
                height=settings.CONSTANT["VIDEO"]["HEIGHT"],
                file='/upload/videos/2018/10/01/video.mp4',
                size=settings.CONSTANT["VIDEO"]["SIZE"],
            )
            self.video_admin.genres.add(self.genre1)
            self.video_admin.genres.add(self.genre2)

            self.video_user = Video.objects.create(
                title='video test 2',
                description='description test 2',
                owner=self.user,
                duration=1415.081748,
                width=settings.CONSTANT["VIDEO"]["WIDTH"],
                height=settings.CONSTANT["VIDEO"]["HEIGHT"],
                file='/upload/videos/2018/10/01/video.mp4',
                size=settings.CONSTANT["VIDEO"]["SIZE"]
            )

            self.video_user_inactif = Video.objects.create(
                title='video test 2',
                description='description test 2',
                owner=self.user,
                duration=1415.081748,
                width=settings.CONSTANT["VIDEO"]["WIDTH"],
                height=settings.CONSTANT["VIDEO"]["HEIGHT"],
                file='/upload/videos/2018/10/01/video.mp4',
                size=settings.CONSTANT["VIDEO"]["SIZE"],
                is_actived=subscription_date,
            )

            self.video_user_inactif = Video.objects.create(
                title='video test 2',
                description='description test 2',
                owner=self.user,
                duration=1415.081748,
                width=settings.CONSTANT["VIDEO"]["WIDTH"],
                height=settings.CONSTANT["VIDEO"]["HEIGHT"],
                file='/upload/videos/2018/10/01/video.mp4',
                size=settings.CONSTANT["VIDEO"]["SIZE"],
                # is_actived=subscription_date,
                is_deleted=subscription_date
            )

    # TODO: create video test
    # def test_create_new_video_with_permission(self):
        # path_video = 'media/upload/2019/01/15/video.mp4'

        # file_mock = mock.MagicMock(spec=File)
        # file_mock.filename = 'video.mp4'
        # self.client.force_authenticate(user=self.admin)
        # with open(__file__, 'rb') as fp:
        #     data = {
        #         'file': fp,
        #     }
        #
        #     response = self.client.post(
        #         reverse('video:videos'),
        #         data,
        #         format='json',
        #         # content_type=client.MULTIPART_CONTENT,
        #         Content_disposition =
        #   'form-data; name="file"; filename="video.mp4"'
        #     )
        #
        #     print(response.data)

    def test_list_videos_with_permissions(self):
        """
        Ensure we can list all videos. (ordered by date_created by default)
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('video:videos'),
            format='json',
        )
        content = json.loads(response.content)
        # print(content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 4)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'title', 'owner', 'description', 'height',
                      'is_created', 'is_active', 'is_delete', 'width',
                      'size', 'duration', 'is_actived', 'is_deleted',
                      'file', 'genres', 'hostPathFile',
                      'durationToHMS']

        for key in content['results'][0].keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key),
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes),
        )

    def test_list_active_videos(self):
        """
        Ensure we can list all videos actived.
        (ordered by date_created by default)
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse('video:videos'),
            data={
                "is_actived": True
            },
            format='json',
        )

        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['count'], 1)

        # Check the system doesn't return attributes not expected
        attributes = ['id', 'title', 'owner', 'description', 'height',
                      'is_created', 'is_active', 'is_delete', 'width',
                      'size', 'duration', 'is_actived', 'is_deleted',
                      'file', 'genres', 'hostPathFile', 'durationToHMS']

        for key in content['results'][0].keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key),
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes),
        )
