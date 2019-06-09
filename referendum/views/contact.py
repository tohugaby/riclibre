"""
Referendum's app : Contact views
"""
from django.conf import settings
from django.contrib import messages
from django.views.generic import FormView

from referendum.forms import ContactForm


class ContactView(FormView):
    """
    A contact form view
    """
    SUCCESS_MESSAGE = "Votre question a bien été transmise à l'administrateur du site."
    form_class = ContactForm
    success_url = '/contact'
    template_name = 'referendum/contact.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if settings.DESACTIVATE_RECAPTCHA:
            del form.fields['captcha']
        return form

    def form_valid(self, form):
        form.send_mail()
        messages.add_message(
            self.request,
            messages.INFO,
            self.SUCCESS_MESSAGE
        )
        return super().form_valid(form)
