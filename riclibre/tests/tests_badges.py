"""
Project tests: Badges and achievements relative tests
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from id_card_checker.models import IdCard
from referendum.models import Referendum, Like, Comment, VoteToken


class BadgeMethodTestCase(TestCase):
    """
    Test Badges
    """
    fixtures = ['test_data.json', ]

    def setUp(self) -> None:
        self.user = get_user_model().objects.filter(is_superuser=False).first()
        for achievement in self.user.achievement_set.all():
            achievement.delete()

    def test_user_activation_achievement(self):
        """
        Test user activation related achievement.
        """
        self.assertFalse(self.user.achievement_set.all().exists())
        self.user.is_active = False
        self.user.save()
        self.assertFalse(self.user.achievement_set.all().exists())
        self.user.is_active = True
        self.user.save()
        self.assertTrue(self.user.achievement_set.filter(badge='utilisateur').exists())

    def test_citizen_achievement(self):
        """
        Test valid id card related achievement.
        """
        self.assertFalse(self.user.achievement_set.all().exists())
        id_card = IdCard.objects.create(user=self.user)
        self.assertEqual(id_card.status, IdCard.FAILED)
        self.assertFalse(self.user.achievement_set.all().exists())
        id_card.status = IdCard.SUCCESS
        id_card.save()
        self.assertTrue(self.user.achievement_set.filter(badge='citoyen').exists())

    def test_referendum_achievements(self):
        """
        Test referendum publication and plannification related achievement.
        """
        self.assertFalse(self.user.achievement_set.all().exists())
        referendum = Referendum.objects.create(title='test', description='test', question='test?', creator=self.user)
        self.assertFalse(self.user.achievement_set.all().exists())
        referendum.publication_date = timezone.now()
        referendum.save()
        self.assertTrue(self.user.achievement_set.filter(badge='orateur').exists())
        referendum.event_start = timezone.now()
        referendum.save()
        self.assertTrue(self.user.achievement_set.filter(badge='politicien').exists())

    def test_like_achievements(self):
        """
        Test like related achievement.
        """
        self.assertFalse(self.user.achievement_set.all().exists())
        referendum = Referendum.objects.create(title='test', description='test', question='test?', creator=self.user)
        Like.objects.create(referendum=referendum, user=self.user)
        self.assertTrue(self.user.achievement_set.filter(badge='sympathisant').exists())

    def test_comment_achievements(self):
        """
        Test comment related achievement.
        """
        self.assertFalse(self.user.achievement_set.all().exists())
        referendum = Referendum.objects.create(title='test', description='test', question='test?', creator=self.user)
        Comment.objects.create(referendum=referendum, user=self.user, text='commentaire de test')
        self.assertTrue(self.user.achievement_set.filter(badge='participant').exists())

    def test_vote_achievements(self):
        """
        Test comment related achievement.
        """
        self.assertFalse(self.user.achievement_set.all().exists())
        referendum = Referendum.objects.create(title='test', description='test', question='test?', creator=self.user)
        token = VoteToken.objects.create(referendum=referendum, user=self.user)
        self.assertFalse(self.user.achievement_set.all().exists())
        token.voted = True
        token.save()
        self.assertTrue(self.user.achievement_set.filter(badge='votant').exists())
