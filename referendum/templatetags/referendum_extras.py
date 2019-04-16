"""
Referendum's app: template's custom filters and tags
"""
from django import template
from django.contrib.auth.models import AnonymousUser

from referendum.models import VoteToken

register = template.Library()


@register.filter
def order(value_list, sort_key):
    """
    Sort a list by provided arg.
    :param value_list: object list to sort
    :param sort_key: field used to sort
    :return: a sorted list of object
    """
    return sorted(value_list, key=lambda a: getattr(a, sort_key), reverse=True)


@register.filter
def verbose_name_filter(obj, field_name):
    """
    Get the verbose name of a field.
    :param obj: object owning the field
    :param field_name: field name
    :return: a field verbose name
    """
    return obj._meta.get_field(field_name).verbose_name


@register.simple_tag
def user_has_voted(referendum, user):
    """
    Check if a given user has voted for a given referendum.
    :param referendum: a Referendum instance.
    :param user: a user model instance.
    :return: a boolean
    """
    if isinstance(user,AnonymousUser):
        return False
    try:
        token = VoteToken.objects.get(referendum=referendum, user=user)
        return token.voted
    except VoteToken.DoesNotExist as vote_token_dne:
        return False
