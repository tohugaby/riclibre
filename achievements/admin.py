"""
Achievement's app: Admin config
"""

from django.contrib import admin

from achievements.models import Achievement


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """
    admin class for Achievement model.
    """
    list_display = ("user", "creation_date", "badge")
    list_filter = ("user", "creation_date", "badge")
    search_fields = ("user", "badge")
