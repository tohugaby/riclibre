"""
Referendum's app: tests module for contact view test
"""
import os
import unittest

from django.core import mail
from django.test import TestCase, Client, override_settings
from django.urls import reverse


class ContactViewTestCase(TestCase):
    """
   Test ContactView.
   """

    def setUp(self) -> None:
        self.client = Client()

    @unittest.skipIf(os.getenv('DJANGO_SETTINGS_MODULE') == 'riclibre.settings.travis', "Skip this test on travis")
    @override_settings(DESACTIVATE_RECAPTCHA=True)
    def test_contact_form(self):
        """
        Test contact form and email sending.
        """
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(reverse('contact'), {'email': 'test@test.fr', 'text': 'test'})
        self.assertRedirects(response, reverse('contact'), status_code=302, target_status_code=200, msg_prefix='',
                             fetch_redirect_response=True)
        self.assertEqual(len(mail.outbox), 1)
