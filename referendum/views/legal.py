"""
Referendum's app: Legal view module
"""
import logging

from django.utils import timezone
from django.views.generic import TemplateView

from referendum.models import Referendum

LOGGER = logging.getLogger(__name__)


class LegalView(TemplateView):
    """
    Referendum's app legal view.
    """
    template_name = 'referendum/legal.html'

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)
        return context
