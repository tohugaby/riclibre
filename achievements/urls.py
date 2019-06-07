from django.urls import path

from achievements.views import AchievementsView

urlpatterns = [
    path('success', AchievementsView.as_view(), name='achievements')
]