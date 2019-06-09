"""
Referendum's app: contact 's forms
"""
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django import forms
from django.conf import settings
from django.core.mail import send_mail


class ContactForm(forms.Form):
    """
    Contact form
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label="Votre adresse mail")
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label="Votre question")
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def send_mail(self):
        """
        Send mail to admin.
        """
        clean_text = self.cleaned_data['text']
        clean_email = self.cleaned_data['email']
        send_mail(
            'Formulaire de contact:%s' % clean_email,
            'Demande de %s : %s ' % (clean_email, clean_text),
            'contact@%s' % settings.MAIL_DOMAIN,
            [admin[1] for admin in settings.ADMINS],
            fail_silently=False,
        )
