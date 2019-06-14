"""
Referendum's app: Referendum's views
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import DateTimeInput
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from tempus_dominus.widgets import DateTimePicker

from referendum.forms import VoteForm, CommentForm
from referendum.models import Referendum, Category, VoteToken, Choice

LOGGER = logging.getLogger(__name__)


class ReferendumListView(ListView):
    """
    Referendum list view
    """
    model = Referendum
    template_name = 'referendum/referendum_list.html'
    queryset = Referendum.objects.filter(publication_date__isnull=False, publication_date__lte=timezone.now())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Liste des référendums"
        return context


class InProgressReferendumListView(ListView):
    """
    In progress referendum list view
    """
    model = Referendum
    template_name = 'referendum/referendum_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Liste des référendums en cours de vote"
        return context

    def get_queryset(self):
        return [referendum for referendum in Referendum.objects.all() if referendum.is_in_progress]


class OverReferendumListView(ListView):
    """
    Over referendum list view
    """
    model = Referendum
    template_name = 'referendum/referendum_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Liste des référendums terminés"
        return context

    def get_queryset(self):
        return [referendum for referendum in Referendum.objects.all() if referendum.is_over]


class FavoritesReferendumListView(LoginRequiredMixin, ListView):
    """
    Favorites referendum list view
    """
    model = Referendum
    template_name = 'referendum/referendum_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Les référendums que vous avez liké"
        return context

    def get_queryset(self):
        return sorted([like.referendum for like in self.request.user.like_set.all()], key=lambda x: x.event_start,
                      reverse=True)


class UserVotedForReferendumListView(LoginRequiredMixin, ListView):
    """
    Referendum for those user has voted list view
    """
    model = Referendum
    template_name = 'referendum/referendum_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Les référendums pour lesquels vous avez voté"
        return context

    def get_queryset(self):
        return sorted([token.referendum for token in self.request.user.votetoken_set.filter(voted=True)],
                      key=lambda x: x.event_start,
                      reverse=True)


class CategoryView(ListView):
    """
    Categories Referendum list view
    """
    model = Category
    template_name = 'referendum/referendum_list.html'

    def get_object(self):
        """
        Get category.
        :return: Category instance
        """
        return self.model.objects.get(slug=self.kwargs['slug'])

    def get_queryset(self):
        return self.get_object().referendum_set.filter(publication_date__isnull=False,
                                                       publication_date__lte=timezone.now())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Liste des référendums dans la catégorie {}".format(self.get_object().title.lower())
        return context


class MyReferendumsView(LoginRequiredMixin, ListView):
    """
    User's referendums list view
    """
    model = Referendum
    template_name = 'referendum/referendum_list.html'

    def get_queryset(self):
        return Referendum.objects.filter(creator=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['title'] = "Mes référendums"
        return context


class ReferendumDetailView(DetailView):
    """
    Referendum detail view
    """
    model = Referendum
    template_name = 'referendum/referendum_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = self.get_comment_form()
        return context

    def get_comment_form(self):
        """
        Get an instance of comment form.
        """
        form = CommentForm(initial={'referendum': self.object.pk})
        return form


class ReferendumCreateView(LoginRequiredMixin, CreateView):
    """
    Referendum crete view
    """
    model = Referendum
    fields = ["title", "description", "question", "categories"]
    template_name = 'referendum/referendum_create.html'

    def get_form_class(self):
        form_class = super().get_form_class()
        for field_name, field in form_class.base_fields.items():
            field.widget.attrs['class'] = 'form-control'
        return form_class

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.object.get_absolute_url())


class ReferendumUpdateView(LoginRequiredMixin, UpdateView):
    """
    Referendum update view
    """
    model = Referendum
    fields = []
    template_name = 'referendum/referendum_update.html'

    def get_fields(self):
        """
        Get form field according to referendum state.
        :return:
        """
        self.fields = self.object.get_updatable_fields()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self.object.creator == request.user:
            raise PermissionDenied
        return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if not self.object.creator == request.user:
            raise PermissionDenied
        return response

    def get_form_class(self):
        self.get_fields()
        form_class = super().get_form_class()
        for field_name, field in form_class.base_fields.items():
            if isinstance(field.widget, DateTimeInput):
                options = dict(format='DD/MM/YYYY', locale='fr')
                min_date = timezone.now().strftime('%Y-%m-%d')
                options['minDate'] = min_date
                field.help_text = "La date de minimum de publication est le %s." % timezone.now().strftime('%d/%m/%Y')
                if field_name == 'event_start':
                    min_date = self.object.minimum_event_start_date.strftime('%Y-%m-%d')
                    options['minDate'] = min_date
                    min_delay_before_event = self.object.get_min_delay_before_event_start()
                    field.help_text = self.object.VALIDATION_MESSAGES['pub_gte_start'] % min_delay_before_event
                field.widget = DateTimePicker(
                    options=options,
                    attrs={
                        'append': 'fa fa-calendar',
                        'icon_toggle': True,
                    })

            else:
                field.widget.attrs['class'] = 'form-control'
        return form_class

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form))


class VoteControlView(DetailView):
    """
    Control that user is allowed to vote and redirect him/her to vote page.
    """
    model = Referendum
    template_name = 'referendum/referendum_vote_control.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.object.is_in_progress and self.request.user.has_perm('referendum.is_citizen'):
            vote_token, created = VoteToken.objects.get_or_create(user=self.request.user, referendum=self.object)
            return redirect(reverse_lazy('vote', kwargs={'token': vote_token.token}))
        return response


class ReferendumVoteView(FormMixin, DetailView):
    """
    Vote view
    """
    slug_field = 'token'
    slug_url_kwarg = 'token'
    model = VoteToken
    template_name = 'referendum/referendum_vote.html'
    form_class = VoteForm

    def check_user_is_citizen(self):
        """
        Check if user has citizen perm
        :return: A boolean
        """
        return self.request.user.has_perm('referendum.is_citizen')

    def get_vote_token(self):
        """
        Get the user vote token for given referendum.
        :return: a vote_token instance
        """
        return self.model.objects.get(token=self.kwargs['token'])

    def check_token_user_is_request_user(self):
        """
        Check vote token validity.
        :return: A boolean
        """
        token_user = self.get_vote_token().user
        return token_user == self.request.user

    def get_success_url(self):
        return reverse_lazy('referendum', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['token'] = self.kwargs['token']
        context['can_vote'] = self.check_user_is_citizen()
        context['valid_token'] = self.check_token_user_is_request_user()
        context['already_voted'] = self.get_vote_token().voted
        return context

    def post(self, request, *args, **kwargs):
        """
        Custom post method in detailview
        """
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_object(self, queryset=None):
        return self.get_vote_token().referendum

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        choices = [(choice.id, choice.title) for choice in self.object.choice_set.all()]
        form.fields['choice'].choices = choices
        return form

    def form_valid(self, form):
        choice = Choice.objects.get(pk=form.cleaned_data['choice'])
        self.get_vote_token().vote(choice=choice)
        return super().form_valid(form)
