"""
Referendum's app: tests module for like view
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver

from referendum.models import Referendum, Like

LOGGER = logging.getLogger(__name__)


class LikeViewTestCase(TestCase):
    """
    Test LikeView.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.client = Client()
        self.user = get_user_model().objects.first()
        self.referendum = Referendum.objects.first()

    def test_like_referendum(self):
        """
        Test when user add a like to a referendum.
        """
        self.client.force_login(self.user)
        nb_like = self.referendum.like_set.count()
        response = self.client.get(reverse('like', kwargs={'slug': self.referendum.slug}))
        self.referendum.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(nb_like + 1, self.referendum.like_set.count())

    def test_unlike_referendum(self):
        """
        Test when user remove a like to a referendum.
        """
        self.client.force_login(self.user)
        Like.objects.create(referendum=self.referendum, user=self.user)
        nb_like = self.referendum.like_set.count()
        response = self.client.get(reverse('like', kwargs={'slug': self.referendum.slug}))
        self.referendum.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(nb_like - 1, self.referendum.like_set.count())

    def test_anonymous_user_is_redirect_to_login(self):
        """
        Test when anonymous user try to like a referendum.
        """
        nb_like = self.referendum.like_set.count()
        response = self.client.get(reverse('like', kwargs={'slug': self.referendum.slug}))
        self.referendum.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(nb_like, self.referendum.like_set.count())


class LikeViewLiveTestCase(StaticLiveServerTestCase):
    """
    Test LikeView with selenium.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.client = Client()
        self.referendum = Referendum.objects.first()
        self.user = get_user_model().objects.first()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(2)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def force_login_user(self):
        """
        helper to force user login
        :return:
        """
        self.client.force_login(self.user)
        cookie = self.client.cookies['sessionid']
        self.selenium.get(self.live_server_url)
        self.selenium.add_cookie(
            {
                'name': 'sessionid',
                'value': cookie.value,
                'secure': False,
                'path': '/'
            }
        )
        self.selenium.refresh()

    def test_like_referendum(self):
        """
        Test when user like a referendum
        """
        nb_like = self.referendum.like_set.count()
        self.force_login_user()
        self.selenium.get("%s%s" % (self.live_server_url, self.referendum.get_absolute_url()))
        like_btn = self.selenium.find_element_by_id('like-btn')
        like_btn.click()
        self.referendum.refresh_from_db()
        self.assertEqual(nb_like + 1, self.referendum.like_set.count())

    def test_unlike_referendum(self):
        """
        Test when user unlike a referendum
        """
        Like.objects.create(user=self.user, referendum=self.referendum)
        nb_like = self.referendum.like_set.count()
        self.force_login_user()
        self.selenium.get("%s%s" % (self.live_server_url, self.referendum.get_absolute_url()))
        like_btn = self.selenium.find_element_by_id('like-btn')
        like_btn.click()
        self.referendum.refresh_from_db()
        self.assertEqual(nb_like - 1, self.referendum.like_set.count())

    def test_no_like_button_for_anonymous_user(self):
        """
        Test that there is no like button if user is not authenticated.
        """
        self.selenium.get("%s%s" % (self.live_server_url, self.referendum.get_absolute_url()))
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_id('like-btn')
