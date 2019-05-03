import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.template.defaultfilters import date as _date, time as _time
from django.views.generic import UpdateView, FormView

from referendum.forms import CommentForm
from referendum.models import Comment

LOGGER = logging.getLogger(__name__)


def get_serialized_comment(comment):
    """
    Get a dict of comment instance.
    :param comment: Comment instance.
    :return: a dict representation of a comment.
    """
    return {
        'pk': comment.pk,
        'text': comment.text,
        'author': comment.user.username,
        'publication_date': _date(comment.publication_date),
        'publication_time': _time(comment.publication_date),
        'last_update_date': _date(comment.last_update),
        'last_update_time': _time(comment.last_update),
        'update_url': comment.update_url

    }


class CommentCreateView(LoginRequiredMixin, FormView):
    model = Comment
    template_name = 'referendum/snippets/comment_form.html'
    form_class = CommentForm

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        self.object = Comment.objects.create(user=self.request.user, referendum_id=form.cleaned_data['referendum'],
                                             text=form.cleaned_data['text'])
        serialized_object = get_serialized_comment(self.object)

        return JsonResponse(serialized_object)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'referendum/snippets/comment_form.html'
    fields = ['text']

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        super().form_valid(form)
        serialized_object = get_serialized_comment(self.object)
        return JsonResponse(serialized_object)
