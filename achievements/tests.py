"""
Achievements app: tests module
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from achievements.helpers.badges import BADGES
from achievements.models import Achievement


class AchievementViewsTestCase(TestCase):
    """
    Test Achievements view.
    """
    fixtures = ['test_data.json', ]

    def setUp(self) -> None:
        self.user = get_user_model().objects.filter(is_superuser=False).first()

    def test_achievements_data(self):
        """
        Test that view provides relevant data according to user achievements.
        """
        achievement = Achievement.objects.create(user=self.user, badge=BADGES[0][0])
        self.client.force_login(self.user)
        response = self.client.get(reverse('achievements'))
        view_achievements = response.context_data['object_list']
        user_achievements = [badge['title'] for badge in filter(lambda x: x['success'] == True, view_achievements)]
        self.assertIn(achievement.badge, user_achievements)
