"""
Referendum's app: referendum 's forms
"""
from django import forms
from django.forms import Select


class VoteForm(forms.Form):
    """
    Vote form
    """
    choice = forms.ChoiceField(
        widget=Select(attrs={'class': 'form-control offset-lg-4 col-lg-4 offset-md-3 col-md-6 col-12'}),
        label="Vote"
    )


class CommentForm(forms.Form):
    """
    Comment form
    """
    referendum = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'form-control'}), label="Référendum")
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label="Commentaire")
