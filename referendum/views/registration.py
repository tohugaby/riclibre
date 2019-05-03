"""
Referendum's app : Registration views
"""
import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView, TemplateView, DetailView, FormView

from referendum.forms import SignupForm, ActivationForm
from referendum.utils import send_validation_email, AccountActivationTokenGenerator
from referendum.views.utils import UserIsAnonymousMixin

LOGGER = logging.getLogger(__name__)


class SignupView(UserIsAnonymousMixin, CreateView):
    """
    Referendum's app main view.
    """
    template_name = 'registration/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('signup_confirm')

    def form_valid(self, form):
        """
        Override form_valid method to change user is_active status
        :param form:
        :return:
        """
        self.object = form.save(commit=False)
        self.object.is_active = False
        self.object.save()
        # send email for account activation
        send_validation_email(self.object.email, self.request)
        return super().form_valid(form)


class SignupConfirmView(UserIsAnonymousMixin, TemplateView):
    """
    Confirm sign up success.
    """
    template_name = 'registration/signup_confirm.html'


class AskAccountActivationView(UserIsAnonymousMixin, FormView):
    """
    Allows user to ask account's validation email.
    """
    template_name = 'registration/account_activation_form.html'
    form_class = ActivationForm
    success_url = reverse_lazy('signup_confirm')

    def post(self, request, *args, **kwargs):
        """
        Override post method. Send mail if form is valid.
        """
        form = self.get_form()
        if form.is_valid():
            send_validation_email(form.cleaned_data['email'], self.request)
        return super().post(request, *args, **kwargs)


class AccountActivationView(UserIsAnonymousMixin, DetailView):
    """
    Make user account active if token is valid.
    """
    template_name = 'registration/account_activation.html'
    model = get_user_model()

    def get(self, request, *args, **kwargs):
        """
        Override get method. Activate user account if token is valid.
        """
        response = super().get(request, *args, **kwargs)
        if self.token_valid():
            self.object.is_active = True
            self.object.save()
        return response

    def get_object(self, queryset=None):
        """
        Get object from kwargs uid.
        """
        return self.get_user(self.kwargs['uidb64'])

    def get_context_data(self, **kwargs):
        """
        Override get_context_data method by adding valid_token.
        """
        context = super().get_context_data(**kwargs)
        context['valid_token'] = self.token_valid() and not self.object.is_active
        return context

    def token_valid(self):
        """
        Check token validity.
        :return:
        """
        user = self.get_user(self.kwargs['uidb64'])
        token = self.kwargs['token']
        return AccountActivationTokenGenerator().check_token(user, token)

    def get_user(self, uidb64):
        """
        Get user instance from uidb64.
        :param uidb64: base64 encoded user primary key.
        :return: user instance.
        """
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model()._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist, ValidationError):
            user = None
        return user
