"""
Referendum's app : Account views
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from referendum.forms import AccountUpdateForm


class AccountView(LoginRequiredMixin, UpdateView):
    """
    Account view.
    """
    model = get_user_model()
    template_name = 'referendum/account.html'
    form_class = AccountUpdateForm

    def get_success_url(self):
        return reverse_lazy('account', kwargs={'pk': self.object.pk})
