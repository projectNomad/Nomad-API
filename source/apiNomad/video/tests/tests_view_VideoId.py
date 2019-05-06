import json

from unittest import mock
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.test.utils import override_settings
from django.db.models import signals

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apiNomad.factories import AdminFactory, UserFactory
from video.models import Video


class VideosTests(APITestCase):

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

        self.pre_signals = (
            len(signals.pre_delete.receivers),
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
                size=settings.CONSTANT["VIDEO"]["SIZE"]
            )

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

            self.video_user_actif = Video.objects.create(
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

            self.video_user_delete = Video.objects.create(
                title='video test 2',
                description='description test 2',
                owner=self.user,
                duration=1415.081748,
                width=settings.CONSTANT["VIDEO"]["WIDTH"],
                height=settings.CONSTANT["VIDEO"]["HEIGHT"],
                file='/upload/videos/2018/10/01/video.mp4',
                size=settings.CONSTANT["VIDEO"]["SIZE"],
                is_actived=subscription_date,
                is_deleted=subscription_date
            )

    def test_retrieve_video_id_not_exist(self):
        """
        Ensure we can't retrieve an video that doesn't exist.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'video:videos_id',
                kwargs={'pk': 999},
            ),
            format='json',
        )

        content = {"detail": _("Not found.")}

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), content)

    @override_settings(
        TIME_ZONE='UTC'
    )
    def test_retrieve_video(self):
        """
        Ensure we can retrieve an event.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                'video:videos_id',
                kwargs={'pk': self.video_admin.id},
            )
        )

        result = json.loads(response.content)

        self.assertEqual(result['id'], self.video_admin.id)
        self.assertEqual(result['title'], self.video_admin.title)
        self.assertEqual(result['description'], self.video_admin.description)
        self.assertEqual(
            result['is_created'],
            self.video_admin.is_created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        self.assertEqual(result['owner']['id'], self.video_admin.owner.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(
        TIME_ZONE='UTC'
    )
    def test_update_video_with_permission(self):
        """
        Ensure we can update a specific video.
        """
        title = 'new title video'
        description = 'new description video'
        data_post = {
            "title": title,
            "description": description,
        }

        self.admin.is_superuser = True
        self.admin.save()

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'video:videos_id',
                kwargs={'pk': self.video_admin.id},
            ),
            data_post,
            format='json',
        )

        result = json.loads(response.content)

        self.assertEqual(result['id'], self.video_admin.id)
        self.assertEqual(result['title'], title)
        self.assertEqual(result['description'], description)
        self.assertEqual(
            result['is_created'],
            self.video_admin.is_created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(result['owner']['id'], self.video_admin.owner.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_video_without_permission(self):
        """
        Ensure we can't update a specific event without permission.
        """
        title = 'new title video'
        description = 'new description video'
        data_post = {
            "title": title,
            "description": description,
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse(
                'video:videos_id',
                kwargs={'pk': self.video_user.id},
            ),
            data_post,
            format='json',
        )

        content = {
            'detail': 'You are not authorized to update a given video.'
        }
        self.assertEqual(json.loads(response.content), content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_video_that_doesnt_exist(self):
        """
        Ensure we can't update a specific video if it doesn't exist.
        """
        data_post = {
            "title": 'new title',
        }

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse(
                'video:videos_id',
                kwargs={'pk': 9999},
            ),
            data_post,
            format='json',
        )

        content = {'detail': _("Not found.")}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_video_with_permission(self):
        """
        Ensure we can delete a specific video.
        """
        self.client.force_authenticate(user=self.admin)

        try:
            response = self.client.delete(
                reverse(
                    'video:videos_id',
                    kwargs={'pk': self.video_user.id},
                ),
            )
            self.assertEqual(response.content, b'')
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        except FileNotFoundError:
            pass

    def test_delete_video_without_permission(self):
        """
        Ensure we can't delete a specific video without permission.
        """
        data = []

        def pre_delete_handler(signal, sender, instance, **kwargs):

            data.append(
                (instance, sender, kwargs.get("raw", False))
            )

        signals.pre_delete.connect(pre_delete_handler, weak=False)

        self.client.force_authenticate(user=self.user)

        try:

            response = self.client.delete(
                reverse(
                    'video:videos_id',
                    kwargs={'pk': self.video_admin.id},
                ),
            )

            content = {
                'detail': 'You do not have permission to perform this action.'
            }
            self.assertEqual(json.loads(response.content), content)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        except FileNotFoundError:
            pass
        finally:
            signals.pre_delete.disconnect(pre_delete_handler)

    def test_delete_video_that_doesnt_exist(self):
        """
        Ensure we can't delete a specific video if it doesn't exist
        """
        data = []

        def pre_delete_handler(signal, sender, instance, **kwargs):

            data.append(
                (instance, sender, kwargs.get("raw", False))
             )

        signals.pre_delete.connect(pre_delete_handler, weak=False)

        self.client.force_authenticate(user=self.admin)

        try:
            response = self.client.delete(
                reverse(
                    'video:videos_id',
                    kwargs={'pk': 9999},
                ),
            )
            content = {'detail': _("Not found.")}
            self.assertEqual(json.loads(response.content), content)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        except FileNotFoundError:
            pass
        finally:
            signals.pre_delete.disconnect(pre_delete_handler)

    def tearDown(self):
        """
        Save up the number of connected signals so that we can check at the
        end that all the signals we register get properly unregistered
        """
        post_signals = (
           len(signals.pre_delete.receivers),
        )

        self.assertEqual(self.pre_signals, post_signals)
