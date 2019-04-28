"""
Referendum's app: Referendum's model's tests
"""

import logging

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from referendum.models import Referendum, Vote, Choice
from referendum.tests import get_referendum_test_data, create_test_user

LOGGER = logging.getLogger(__name__)


class ReferendumTestCase(TestCase):
    """
    Test Referendum model and its methods.
    """
    fixtures = ['test_data.json']

    def setUp(self):
        """

        :return:
        """
        self.password = 'Azer123@'
        self.user = create_test_user(self.password)
        self.referendum_data = get_referendum_test_data(self.user)

    def test_create(self):
        """
        Test referendum creation
        :return:
        """
        nb_referendum_before = Referendum.objects.count()
        Referendum.objects.create(**self.referendum_data)
        self.assertGreater(Referendum.objects.count(), nb_referendum_before)

    def test_update_referendum_when_not_published(self):
        """
        Test referendum instance update when it 's not published.
        :return:
        """
        new_referendum = Referendum.objects.create(**self.referendum_data)
        old_value = new_referendum.title
        new_referendum.title = "nouveau titre"
        self.assertNotEqual(old_value, new_referendum.title)

    def test_can_not_update_referendum_when_published(self):
        """
        Test referendum instance update when it 's not published.
        :return:
        """
        # Create referendum instance
        new_referendum = Referendum.objects.create(**self.referendum_data)
        # Update publication date
        new_referendum.publication_date = timezone.now()
        # Save publication date update
        new_referendum.save()

        old_value = new_referendum.title

        # Update referendum title
        new_referendum.title = "nouveau titre"
        # Save title update
        new_referendum.save()

        # Refresh from values from db
        new_referendum.refresh_from_db()
        self.assertEqual(old_value, new_referendum.title)

    def test_can_update_referendum_when_published_later(self):
        """
        Test referendum instance update when it will be published later
        :return:
        """
        # Create referendum instance
        new_referendum = Referendum.objects.create(**self.referendum_data)
        # Update publication date
        new_referendum.publication_date = timezone.now() + timezone.timedelta(days=20)
        # Save publication date update
        new_referendum.save()

        old_value = new_referendum.title

        # Update referendum title
        new_referendum.title = "nouveau titre"
        # Save title update
        new_referendum.save()

        # Refresh from values from db
        new_referendum.refresh_from_db()
        self.assertNotEqual(old_value, new_referendum.title)

    def test_can_not_update_referendum_when_started(self):
        """
        Test referendum instance update when it is started
        :return:
        """
        # Create referendum instance
        new_referendum = Referendum.objects.create(**self.referendum_data)
        # Update publication date
        new_referendum.publication_date = timezone.now() - timezone.timedelta(days=2)
        new_referendum.event_start = timezone.now()
        new_referendum.duration = 86399
        # Save publication date update
        new_referendum.save()

        old_value = new_referendum.title

        # Update referendum title
        new_referendum.title = "nouveau titre"
        # Save title update
        new_referendum.save()

        # Refresh from values from db
        new_referendum.refresh_from_db()
        self.assertEqual(old_value, new_referendum.title)

    def test_can_not_update_referendum_when_finished(self):
        """
        Test referendum instance update when it is finished
        :return:
        """
        # Create referendum instance
        new_referendum = Referendum.objects.create(**self.referendum_data)
        # Update publication date
        new_referendum.publication_date = timezone.now() - timezone.timedelta(days=3)
        new_referendum.event_start = timezone.now() - timezone.timedelta(days=2)
        # Save publication date update
        new_referendum.save()

        old_value = new_referendum.title

        # Update referendum title
        new_referendum.title = "nouveau titre"
        # Save title update
        new_referendum.save()

        # Refresh from values from db
        new_referendum.refresh_from_db()
        self.assertEqual(old_value, new_referendum.title)


class ChoiceTestCase(TestCase):
    """
    Test Choice model and its methods.
    """

    def setUp(self):
        self.user = get_user_model().objects.create(username='test', email='test@test.fr', is_active=True)
        self.password = "test"
        self.user.set_password(self.password)
        self.user.save()
        self.new_referendum = Referendum.objects.create(**get_referendum_test_data(self.user))

        self.choices_data = [
            {
                "title": "oui",
                "referendum": self.new_referendum,
                "votes": 8
            },
            {
                "title": "non",
                "referendum": self.new_referendum,
                "votes": 2
            }
        ]

    @staticmethod
    def create_choices_and_votes(*choices_data):
        """
        Helper to create votes
        :return:
        """
        choices = []
        for choice_data in choices_data:
            choice = Choice.objects.create(title=choice_data["title"], referendum=choice_data["referendum"])
            for _ in range(choice_data["votes"] + 1):
                Vote.objects.create(choice=choice)
            choices.append(choice)
        return choices

    def test_nb_votes(self):
        """
        Test nb_votes property.
        :return:
        """

        self.create_choices_and_votes(*self.choices_data)

        choice1 = Choice.objects.get(referendum=self.new_referendum, title="oui")
        choice2 = Choice.objects.get(referendum=self.new_referendum, title="non")

        self.assertGreater(choice1.nb_votes, choice2.nb_votes)

    def test_votes_percentage(self):
        """
        Test votes percentage property.
        :return:
        """

        self.create_choices_and_votes(*self.choices_data)

        choice1 = Choice.objects.get(referendum=self.new_referendum, title="oui")
        choice2 = Choice.objects.get(referendum=self.new_referendum, title="non")

        self.assertGreater(choice1.votes_percentage, choice2.votes_percentage)
