from django.contrib import admin

# Register your models here.
from id_card_checker.models import IdCard


@admin.register(IdCard)
class IdCardAdmin(admin.ModelAdmin):
    """
    Admin class for Idcard model
    """
    search_fields = ("user", "status", "creation", "update", "valid_until", "comment")
    list_display = ("user", "document", "status", "creation", "update", "valid_until", "comment")
    list_filter = ("user", "status", "creation", "update", "valid_until")
    autocomplete_fields = ["user"]
