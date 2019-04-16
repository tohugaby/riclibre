"""
Referendum app: Referendum's models admin representation
"""
from django.contrib import admin
from django.utils.html import format_html

from referendum.models import Referendum, Category, Choice


class ChoiceInline(admin.TabularInline):
    """
    admin Inline for Choice.
    """
    model = Choice


@admin.register(Referendum)
class ReferendumAdmin(admin.ModelAdmin):
    """
    admin class for Referendum model.
    """
    list_display = (
        "title", "question", "creator", "slug", "creation_date", "last_update", "publication_date", "event_start",
        "duration", "event_end", "is_published", "is_in_progress", "is_over", "nb_votes", "results")
    list_filter = ("categories", "creation_date", "last_update", "publication_date", "event_start", "duration")
    search_fields = ("title", "description", "question")
    inlines = [ChoiceInline, ]

    def results(self, obj):
        """
        Display referendum results as string
        :param obj:
        :return:
        """
        return format_html("<br>".join([f"{choice.title} : {choice.votes_percentage}%" for choice in sorted(
            obj.get_results(),
            key=lambda choice:
            choice.nb_votes,
            reverse=True)]))


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    admin class for Category model.
    """
    list_display = ("title", "slug")
    search_fields = ("title",)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """
    admin class for Choice model.
    """
    list_display = ("referendum", "title", "nb_votes", "percentage")
    search_fields = ("referendum", "title")
    autocomplete_fields = ["referendum"]

    def percentage(self, obj):
        """
        display percentage with symbol.
        """
        return f"{obj.votes_percentage}%"

    percentage.short_description = "Pourcentage"
