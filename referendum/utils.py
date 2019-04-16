"""
This module contains various utilities.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Strategy object used to generate and check tokens for the password
    reset mechanism.
    """
    key_salt = "referendum.utils.AccountActivationTokenGenerator"
    secret = settings.SECRET_KEY

    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key and some user state that's sure to change
        after a password reset to produce a token that invalidated when it's
        used:
        """

        return str(user.pk) + str(user.is_active) + str(timestamp)


def get_account_validation_context(email, request):
    """
    Used to get context for account's validation's email context
    :param email: a user email.
    :param request: a request object
    :return: a context dict
    """
    context = {}
    current_site = get_current_site(request)

    user = get_user_model().objects.filter(email=email).first()
    if user:
        context = {'email': email,
                   'site_name': current_site.name,
                   'protocol': 'http' if settings.DEBUG else 'https',
                   'domain': current_site.domain,
                   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                   'token': AccountActivationTokenGenerator().make_token(user)
                   }
    return context


def send_validation_email(email, request):
    """
    Send validation email
    :param email: a user email
    :param request: a request object
    :return:
    """
    email_template_name = 'registration/account_activation_email.html'
    context = get_account_validation_context(email, request)
    send_mail(
        'R.I.C Libre : Activation de votre compte',
        loader.render_to_string(email_template_name, context),
        'activation@riclibre.fr',
        [email])
