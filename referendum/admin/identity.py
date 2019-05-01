"""
Referendum app: Identity's models admin representation
"""

from django.contrib import admin

from referendum.models.identity import Identity


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    """
    admin class for Comment model.
    """
    search_fields = ("user", "valid_until", "creation")
    list_display = ("user", "valid_until", "creation", "is_valid_identity")
    list_filter = ("user", "valid_until", "creation")
    autocomplete_fields = ["user"]
