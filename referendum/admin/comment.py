from django.contrib import admin

from referendum.models import Comment, Report


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    admin class for Comment model.
    """
    search_fields = ("referendum", "user", "text")
    list_display = ("referendum", "user", "text", "publication_date", "last_update", "visible")
    list_filter = ("referendum", "user", "publication_date", "last_update", "visible")
    autocomplete_fields = ["referendum", "user"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    admin class for Report model.
    """
    search_fields = ("comment", "user", "text")
    list_display = ("comment", "user", "text", "creation_date")
    list_filter = ("comment", "user", "text", "creation_date")
    autocomplete_fields = ["comment", "user"]
