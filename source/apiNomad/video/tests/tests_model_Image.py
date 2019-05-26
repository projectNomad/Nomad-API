from rest_framework.test \
    import APITransactionTestCase

from video.models import Image


class ImageTests(APITransactionTestCase):

    def test_create_video(self):
        """
        Ensure we can create a new event with just required arguments
        """
        path_img = 'media/upload/images/videos/2019/01/15/video.jpg'
        image = Image.objects.create(
            file=path_img,
        )

        self.assertEqual(image.file, path_img)
