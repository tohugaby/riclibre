"""
Id_card_checker's app:  IdCard's forms
"""
from django import forms

from id_card_checker.models import IdCard


class IdCardForm(forms.ModelForm):
    """
    IdCard upload form
    """

    class Meta:
        model = IdCard
        fields = ['document']
