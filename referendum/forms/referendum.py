"""
Referendum's app: referendum 's forms
"""
from django import forms
from django.forms import modelform_factory, Select
from django.forms.widgets import ChoiceWidget

from referendum.models import Referendum


# def referendum_form_factory(referendum: Referendum):
#     """
#     Build a form according to referendum state.
#     :param referendum: a Referendum instance.
#     :return: a form instance
#     """
#     form = modelform_factory(Referendum, fields=referendum.get_updatable_fields())
#     return form


class VoteForm(forms.Form):
    choice = forms.ChoiceField(widget=Select(attrs={'class': 'form-control'}),label="Vote")
