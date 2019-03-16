"""
Referendum app: Vote's models admin representation
"""

from django.contrib import admin

from referendum.admin.utils import ReadOnlyModelAdmin
from referendum.models import Vote, VoteToken


@admin.register(Vote)
class VoteModelAdmin(ReadOnlyModelAdmin):
    """
    admin class for Vote model.
    """
    list_display = ("referendum", "choice", "vote_date")
    readonly_fields = ("referendum", "choice", "vote_date")
    search_fields = ("referendum",)
    list_filter = ("vote_date",)


@admin.register(VoteToken)
class VoteTokenAdmin(ReadOnlyModelAdmin):
    """
    admin class for VoteToken model.
    """
    list_display = ("referendum", "user", "token", "voted")
    readonly_fields = ("referendum", "user", "token", "voted")
