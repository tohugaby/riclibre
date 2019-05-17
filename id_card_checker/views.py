# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin

from id_card_checker.forms import IdCardForm
from id_card_checker.models import IdCard


class IdCardUploadView(LoginRequiredMixin, MultipleObjectMixin, MultipleObjectTemplateResponseMixin, CreateView):
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
        for field_name, field in form_class.base_fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.required = True
        return form_class

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(reverse('idcard'))

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        self.object_list = self.get_queryset()
        print(self.object_list)
        return self.render_to_response(self.get_context_data(form=form, object_list=self.get_queryset()))
