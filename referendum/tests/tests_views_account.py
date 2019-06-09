"""
Referendum's app: Test registration views
"""
import logging

from django.conf import settings
from django.test import Client, LiveServerTestCase
from django.urls import reverse

from referendum.tests import create_test_user
from referendum.views.account import AccountView

LOGGER = logging.getLogger(__name__)


class AccountViewTestCase(LiveServerTestCase):
    """
    Test Account view.
    """

    def setUp(self):
        self.client = Client()
        self.password = 'Azer123@'
        self.user = create_test_user(self.password)

    def test_page_access_when_logged_in(self):
        """
        Test access to account page when logged in.
        """
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.get(reverse('account', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_page_access_when_not_logged_in(self):
        """
        Test access to account page when not logged in. Should be redirect.
        """
        response = self.client.get(reverse('account', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         "%s?next=%s" % (settings.LOGIN_URL, reverse('account', kwargs={'pk': self.user.pk})))

    def test_update_account(self):
        """
        Test account update
        """
        self.client.login(username=self.user.email, password=self.password)
        user_initial_first_name = self.user.first_name
        self.assertEqual(user_initial_first_name, '')
        new_user_values = {
            'username': self.user.username,
            'email': self.user.email,
            'first_name': 'leo',
            'last_name': ''
        }
        response = self.client.post(
            reverse('account', kwargs={'pk': self.user.pk}), new_user_values, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, AccountView.as_view().__name__)
        self.user.refresh_from_db()
        self.assertNotEqual(user_initial_first_name, self.user.first_name)
