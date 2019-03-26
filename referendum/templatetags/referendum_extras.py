"""
Referendum's app: template's custom filters and tags
"""
from django import template

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
