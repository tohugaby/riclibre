from django.contrib import admin

# Register your models here.
from referendum.models import Referendum, Category, Choice, Vote, VoteToken, Like, Comment, Report


@admin.register(Referendum)
class ReferendumAdmin(admin.ModelAdmin):
    """
    admin class for Referendum model.
    """
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    admin class for Category model.
    """
    pass


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """
    admin class for Choice model.
    """
    pass


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """
    admin class for Vote model.
    """
    pass


@admin.register(VoteToken)
class VoteTokenAdmin(admin.ModelAdmin):
    """
    admin class for VoteToken model.
    """
    pass


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    admin class for Like model.
    """
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    admin class for Comment model.
    """
    pass


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    admin class for Report model.
    """
    pass
