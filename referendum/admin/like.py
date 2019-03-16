"""
Referendum app: Like's models admin representation
"""

from django.contrib import admin

from referendum.admin.utils import ReadOnlyModelAdmin
from referendum.models import Like


@admin.register(Like)
class LikeAdmin(ReadOnlyModelAdmin):
    """
    admin class for Like model.
    """
    list_display = ('referendum', 'user')
    search_fields = ('referendum', 'user')
