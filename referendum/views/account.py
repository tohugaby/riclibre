"""
Referendum's app : Account views
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView

from referendum.forms import AccountUpdateForm

LOGGER = logging.getLogger(__name__)


class AccountView(LoginRequiredMixin, UpdateView):
    """
    Account view.
    """
    model = get_user_model()
    template_name = 'referendum/account.html'
    form_class = AccountUpdateForm

    def get(self, request, *args, **kwargs):
        if str(request.user.pk) != kwargs['pk']:
            return HttpResponseRedirect(reverse('account', kwargs={'pk': request.user.pk}))
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('account', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id_valid_until'] = self.request.user.identity_set.aggregate(Max('valid_until'))['valid_until__max']
        return context
