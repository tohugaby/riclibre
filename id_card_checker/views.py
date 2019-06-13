"""
Id Card checker app: IdCard views
"""
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin
from kombu.exceptions import OperationalError

from id_card_checker.forms import IdCardForm
from id_card_checker.models import IdCard
from id_card_checker.validators import get_human_readable_file_size, SIZE_LIMITATION_TEXT

LOGGER = logging.getLogger(__name__)


class IdCardUploadView(LoginRequiredMixin, MultipleObjectMixin, MultipleObjectTemplateResponseMixin, CreateView):
    """
    IdCard upload view
    """
    model = IdCard
    form_class = IdCardForm
    template_name = "id_card_checker/id_card_upload.html"

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def get_form_class(self):
        form_class = super().get_form_class()
        max_size_in_mb = None
        if hasattr(settings, 'MAX_ID_CARD_FILE_SIZE'):
            max_size_in_mb = get_human_readable_file_size(settings.MAX_ID_CARD_FILE_SIZE)
        for field_name, field in form_class.base_fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.required = True
            if field_name == 'document' and max_size_in_mb:
                field.help_text = SIZE_LIMITATION_TEXT % max_size_in_mb

        return form_class

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        try:
            self.object.save()
        except OperationalError:
            messages.add_message(self.request, messages.INFO, """Le service de traitement des cartes est momentanément 
            indisponible. Votre carte a bien été enregistrée et sera traitée ultérieurement.""")
        return HttpResponseRedirect(reverse('idcard'))

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        self.object_list = self.get_queryset()
        print(self.object_list)
        return self.render_to_response(self.get_context_data(form=form, object_list=self.get_queryset()))
