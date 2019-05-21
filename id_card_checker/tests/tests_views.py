"""
Id_card_checker's app: Test views
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from id_card_checker.models import IdCard


class IdCardUploadViewTestCase(TestCase):
    """
    Test IdCardUploadView
    """
    fixtures = ['id_card_checker_test_data.json']

    def setUp(self) -> None:
        self.client = Client()
        self.user = get_user_model().objects.first()

    def test_id_card_upload(self):
        """
        Test id card upload.
        """
        nb_id_cards = IdCard.objects.count()
        self.client.force_login(user=self.user)
        with open('./id_card_checker/tests/images/specimen.jpg', 'rb') as id_doc:
            response = self.client.post(reverse('idcard'), {'document': id_doc})
            self.assertEqual(response.status_code, 302)
        self.assertEqual(IdCard.objects.count(), nb_id_cards + 1)

    def test_id_card_failed_upload(self):
        """
        Test id card upload when it failed.
        """
        nb_id_cards = IdCard.objects.count()
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('idcard'), {'document': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(IdCard.objects.count(), nb_id_cards)

    def test_get_id_card_list(self):
        """
        Test id card list view.
        :return:
        """
        id_cards_for_user = self.user.idcard_set.all()
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('idcard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(id_cards_for_user.first(), response.context_data['object_list'])
        self.assertEqual(id_cards_for_user.count(), len(response.context_data['object_list']))
