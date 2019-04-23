"""
Referendum's app: referendum 's forms
"""
from django import forms
from django.forms import Select


class VoteForm(forms.Form):
    choice = forms.ChoiceField(widget=Select(attrs={'class': 'form-control'}), label="Vote")


class CommentForm(forms.Form):
    referendum = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'form-control'}), label="Référendum")
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label="Commentaire")
