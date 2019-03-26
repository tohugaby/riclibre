"""
Referendum's app: registration 's forms
"""
from django import forms
from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm, PasswordResetForm, \
    SetPasswordForm, PasswordChangeForm
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

from referendum.forms.utils import help_text_list_to_span


class CustomLoginForm(AuthenticationForm):
    """
    Custom login form to override widgets.
    """
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control',
                                                           'placeholder': 'email'}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class SignupForm(UserCreationForm):
    """
    User account creation form.
    """
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True,
                                          'class': 'form-control',
                                          'placeholder': 'mot de passe'}),
        help_text=help_text_list_to_span(password_validation.password_validators_help_texts()),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autofocus': True,
                                          'class': 'form-control',
                                          'placeholder': 'mot de passe'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email")
        field_classes = {'username': UsernameField, 'email': EmailField}
        widgets = {
            'username': forms.TextInput(attrs={
                'autofocus': True,
                'class': 'form-control',
                'placeholder': 'nom d\'utilisateur'
            }),
            'email': forms.EmailInput(attrs={
                'autofocus': True,
                'class': 'form-control',
                'placeholder': 'email'
            }),

        }


class AccountUpdateForm(forms.ModelForm):
    """
    User account update form
    """

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name']


class CustomPasswordResetForm(PasswordResetForm):
    """
    Password reset custom form
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'email'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom set password form.
    """
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'mot de passe'}),
        strip=False,
        help_text=help_text_list_to_span(password_validation.password_validators_help_texts())
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'mot de passe'}),
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom chamge password form.
    """

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'mot de passe'}),
        strip=False,
        help_text=help_text_list_to_span(password_validation.password_validators_help_texts())
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'mot de passe'}),
    )

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Ancien mot de '
                                                                                                     'passe'}),
    )


class ActivationForm(forms.Form):
    """
    Activation form.
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'email'})
    )
