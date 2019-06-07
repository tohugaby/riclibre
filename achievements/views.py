"""
Achievements app: achivements view
"""
from django.views.generic import ListView

from achievements.helpers.badges import get_achievements
from achievements.models import Achievement


class AchievementsView(ListView):
    """
    User achievement list.
    """
    template_name = "achievements/achievements.html"

    def get_queryset(self):
        user = self.request.user
        badges = list()
        for key, detail in get_achievements().items():
            badge = {
                'title': key,
                'description': detail[1],
                'success': False,
                'creation_date': None
            }
            try:
                user_badge = user.achievement_set.get(badge=key)
                badge['success'] = True
                badge['creation_date'] = user_badge.creation_date
            except Achievement.DoesNotExist:
                pass
            badges.append(badge)
        return sorted(badges, key=lambda x: x['success'], reverse=True)
