from rest_framework.test \
    import APITransactionTestCase

from video.models import Genre


class EventTests(APITransactionTestCase):
    TITLE = 'event title'
    DESCRIPTION = 'description event'

    def test_create_video(self):
        """
        Ensure we can create a new event with just required arguments
        """

        genre = Genre.objects.create(
            label=self.TITLE,
            description=self.DESCRIPTION,
        )

        self.assertEqual(genre.label, self.TITLE)
        self.assertEqual(genre.description, self.DESCRIPTION)
