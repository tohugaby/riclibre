"""
Referendum's app: Vote's model's tests
"""

import logging
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from referendum.exceptions import UserHasAlreadyVotedError
from referendum.models import Referendum, VoteToken, Choice, Vote
from referendum.tests import REFERENDUM_DATA, create_test_user

LOGGER = logging.getLogger(__name__)


class VoteTestCase(TestCase):
    """
    Test Vote model and its methods.
    """

    def setUp(self):
        self.new_referendum = Referendum.objects.create(**REFERENDUM_DATA)

        self.choice1 = Choice.objects.create(referendum=self.new_referendum, title='oui')
        self.choice2 = Choice.objects.create(referendum=self.new_referendum, title='non')
        self.password = 'Azer123@'
        self.user = create_test_user(self.password, is_active=False)

    def test_vote_cannot_be_changed(self):
        """
        test that vote's instance's update is forbidden.
        :return:
        """
        self.assertEqual(Vote.objects.count(), 0)
        LOGGER.info("create token")
        token = VoteToken.objects.create(referendum=self.new_referendum, user=self.user)
        LOGGER.info("token vote")
        token.vote(self.choice1)
        self.assertEqual(Vote.objects.count(), 1)
        LOGGER.info("vote select")
        vote = Vote.objects.first()
        LOGGER.info(vote)
        LOGGER.info("vote update choice")
        vote.choice = self.choice2
        LOGGER.info("vote save")
        vote.save()
        LOGGER.info("refresh")
        vote.refresh_from_db()
        self.assertEqual(vote.choice, self.choice1)


class VoteTokenTestCase(TestCase):
    """
    Test VoteToken model and its methods.
    """

    def setUp(self):
        self.new_referendum = Referendum.objects.create(**REFERENDUM_DATA)

        self.choice = Choice.objects.create(referendum=self.new_referendum, title='oui')
        self.password = 'Azer123@'
        self.user = create_test_user(self.password, is_active=False)

    def test_create_token(self):
        """
        test a vote token creation.
        :return:
        """
        for number in range(100):
            user = get_user_model().objects.create(email="%s@test.fr" % number, username="utilisateur %s" % number)
            VoteToken.objects.create(referendum=self.new_referendum, user=user)
        token_value_list = [vote_token['token'] for vote_token in VoteToken.objects.all().values('token')]
        self.assertEqual(len(token_value_list), len(set(token_value_list)))

        with self.assertRaises(IntegrityError):
            VoteToken.objects.create(referendum=self.new_referendum, user=self.user)
            VoteToken.objects.create(referendum=self.new_referendum, user=self.user)

    def test_user_can_vote_if_user_has_never_voted(self):
        """
        test vote if user didn't vote before for the same referendum.
        :return:
        """
        token = VoteToken.objects.create(referendum=self.new_referendum, user=self.user)
        self.assertFalse(token.voted)
        self.assertEqual(self.choice.nb_votes, 0)
        token.vote(self.choice)
        self.assertTrue(token.voted)
        self.assertEqual(self.choice.nb_votes, 1)

    def test_user_can_not_vote_if_user_has_ever_voted(self):
        """
        test vote if user did vote before for the same referendum.
        :return:
        """
        token = VoteToken.objects.create(referendum=self.new_referendum, user=self.user)
        self.assertFalse(token.voted)
        self.assertEqual(self.choice.nb_votes, 0)
        token.vote(self.choice)
        self.assertTrue(token.voted)
        self.assertEqual(self.choice.nb_votes, 1)

        with self.assertRaises(UserHasAlreadyVotedError):
            token.vote(self.choice)

        self.assertTrue(token.voted)
        self.assertEqual(self.choice.nb_votes, 1)

    def test_change_voted_field(self):
        """
        test manual change of field voted.
        :return:
        """
        token = VoteToken.objects.create(referendum=self.new_referendum, user=self.user)
        token.vote(self.choice)
        token.voted = False
        token.save()
        token.refresh_from_db()
        self.assertTrue(token.voted)
