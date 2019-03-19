"""
Referendum's app: template's custom filters and tags
"""
from django import template

register = template.Library()


def order(value, arg):
    """

    :param value:
    :param arg:
    :return:
    """
    return sorted(value, key=lambda a: getattr(a, arg), reverse=True)


register.filter('order', order)
