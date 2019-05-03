"""
Referendum's app: Test registration views
"""
import logging

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, Client, LiveServerTestCase
from django.urls import reverse

from referendum.tests import create_test_user
from referendum.utils import get_account_validation_context
from referendum.validators import RequiredCharactersValidator
from referendum.views import SignupConfirmView, SignupView

LOGGER = logging.getLogger(__name__)


class SignupViewTestCase(TestCase):
    """
    Test class for signup view
    """

    def setUp(self):
        self.client = Client()

    def test_signup(self):
        """
        Test signup with complete and valid data.
        """
        nb_users = get_user_model().objects.count()
        response = self.client.post(reverse('signup'), {'username': 'test', 'email': 'test@test.fr',
                                                        'password1': 'Azer123@', 'password2': 'Azer123@'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, SignupConfirmView.as_view().__name__)
        self.assertEqual(get_user_model().objects.count(), nb_users + 1)

    def test_signup_with_partial_data(self):
        """
        Test signup with partial data.
        """
        nb_users = get_user_model().objects.count()
        response = self.client.post(reverse('signup'), {'email': 'test@test.fr',
                                                        'password1': 'Azer123@', 'password2': 'Azer123@'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, SignupView.as_view().__name__)
        self.assertEqual(get_user_model().objects.count(), nb_users)

    def test_signup_with_bad_password_equality(self):
        """
        Test signup with different password.
        """
        nb_users = get_user_model().objects.count()
        response = self.client.post(reverse('signup'), {'email': 'test@test.fr',
                                                        'password1': 'Azer123@', 'password2': 'Azer456@'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, SignupView.as_view().__name__)
        self.assertEqual(get_user_model().objects.count(), nb_users)

    def test_signup_with_password_not_respecting_validators(self):
        """
        Test signup with invalid password.
        """
        nb_users = get_user_model().objects.count()
        response = self.client.post(reverse('signup'), {'email': 'test@test.fr',
                                                        'password1': 'az', 'password2': 'az'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, RequiredCharactersValidator().message)
        self.assertContains(response, "Ce mot de passe est trop court")
        self.assertEqual(response.resolver_match.func.__name__, SignupView.as_view().__name__)
        self.assertEqual(get_user_model().objects.count(), nb_users)


class SignupConfirmViewTestCase(TestCase):
    """
    Test signup confirm view.
    """

    def setUp(self):
        self.client = Client()
        self.password = "Azer123@"
        self.user = create_test_user(self.password)

    def test_rediction_when_logged_in(self):
        """
        Test redirection to confirm view after signup.
        """
        self.client.login(username=self.user.email, password=self.password)
        response = self.client.get(reverse('signup_confirm'))
        self.assertRedirects(response, reverse('index'))


class AskAccountActivationViewTestCase(LiveServerTestCase):
    """
    Test view that allows to ask account validation.
    """

    def setUp(self):
        self.client = Client()
        self.password = 'Azer123@'
        self.user = create_test_user(self.password, is_active=False)

    def test_ask_activation(self):
        """Test asking for account validation."""
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.post(reverse('ask_account_activation'), {'email': self.user.email})
        email_context = get_account_validation_context(self.user.email, response.wsgi_request)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(email_context['uid'], mail.outbox[0].body)
        self.assertIn(email_context['token'], mail.outbox[0].body)


class AccountActivationViewTestCase(LiveServerTestCase):
    """
    Test account activation view.
    """

    def setUp(self):
        self.client = Client()
        self.password = 'Azer123@'
        self.user = create_test_user(self.password, is_active=False)

    def test_activation_for_inactive_account(self):
        """
        Test account validation with inactive account
        """
        self.assertFalse(self.user.is_active)
        response = self.client.post(reverse('ask_account_activation'), {'email': self.user.email})

        email_context = get_account_validation_context(self.user.email, response.wsgi_request)
        activation_response = self.client.get(reverse('account_activation', kwargs={'uidb64': email_context['uid'],
                                                                                    'token': email_context['token']}))

        self.user.refresh_from_db()

        self.assertTrue(activation_response.context['valid_token'])
        self.assertTrue(self.user.is_active)

    def test_activation_for_already_activated_account(self):
        """
        Test account validation with active account
        """
        account_activated = self.user.is_active = True
        self.user.save()
        response = self.client.post(reverse('ask_account_activation'), {'email': self.user.email})

        email_context = get_account_validation_context(self.user.email, response.wsgi_request)
        activation_response = self.client.get(reverse('account_activation', kwargs={'uidb64': email_context['uid'],
                                                                                    'token': email_context['token']}))

        self.user.refresh_from_db()

        self.assertFalse(activation_response.context['valid_token'])
        self.assertEqual(self.user.is_active, account_activated)
