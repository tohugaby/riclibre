"""
Referendum's app: Index view module
"""
import logging

from django.utils import timezone
from django.views.generic import ListView

from referendum.models import Referendum

LOGGER = logging.getLogger(__name__)


class IndexView(ListView):
    """
    Referendum's app main view.
    """
    template_name = 'referendum/index.html'
    model = Referendum

    def get_queryset(self):
        return self.model.objects.filter(publication_date__lte=timezone.now()).order_by("-creation_date")[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voted_soon'] = [ref for ref in
                                 Referendum.objects.filter(event_start__isnull=False).order_by('event_start') if
                                 not ref.is_over][:3]
        try:
            context['last_result'] = [ref for ref in Referendum.objects.all().order_by('-event_start') if ref.is_over][
                0]
        except IndexError:
            context['last_result'] = None

        return context
