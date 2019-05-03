"""
Referendum's app: tests module for comment view test
"""
import logging

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from referendum.models import Referendum, Comment

LOGGER = logging.getLogger(__name__)


class CommentCreateViewTestCase(TestCase):
    """
    Test CommentCreateView.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.client = Client()
        self.user = get_user_model().objects.first()
        self.referendum = Referendum.objects.first()

    def test_create_comment_with_authenticate_user(self):
        """
        Test comment creation with an authenticated user.
        """
        nb_comment = self.referendum.comment_set.count()
        self.client.force_login(self.user)
        data = {
            "referendum": self.referendum.pk,
            'text': "Ceci est un commentaire de test."
        }
        response = self.client.post(reverse("comment_create"), data=data)
        self.referendum.refresh_from_db()
        last_comment = self.referendum.comment_set.last()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.referendum.comment_set.count(), nb_comment + 1)
        self.assertEqual(last_comment.user, self.user)


class CommentUpdateViewTestCase(TestCase):
    """
    Test CommentCreateView.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.client = Client()
        self.user = get_user_model().objects.first()
        self.referendum = Referendum.objects.first()
        self.comment = Comment.objects.create(user=self.user,
                                              referendum=self.referendum,
                                              text="Ceci est le text de base")

    def test_create_comment_with_authenticate_user(self):
        """
        Test comment creation with an authenticated user.
        """

        self.client.force_login(self.user)
        data = {
            'text': "Ceci est le text modifié"
        }
        response = self.client.post(reverse("comment_update", kwargs={'pk': self.comment.pk}), data=data)
        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.comment.text, data['text'])
