"""
Referendum's app: referendum 's forms
"""
from django import forms


class VoteForm(forms.Form):
    """
    Vote form
    """
    choice = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control offset-lg-4 col-lg-4 offset-md-3 col-md-6 col-12'}),
        label="Vote"
    )
    confirm = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=True,
                                 label="""Je confirme mon vote et comprends que la validation de ce formulaire est
                                 définitive.""",
                                 help_text="""Votre vote va être enregistré de façon totalement anonyme. De ce fait,
                                 il vous sera impossible de le modifier ou de consulter l'historique de vos choix de
                                 vote après validation de ce formulaire.""")

    def clean_confirm(self):
        """
        Check that confirm field is true
        :return:
        """
        data = self.cleaned_data['confirm']
        if data is False:
            raise forms.ValidationError("Vous devez confirmer votre vote")
        return data


class CommentForm(forms.Form):
    """
    Comment form
    """
    referendum = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'form-control'}), label="Référendum")
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label="Commentaire")
