"""
Referendum's app: Referendum's models
"""

import logging
from functools import reduce

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError, transaction
from django.db.models import CASCADE
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from referendum.models.utils import FieldUpdateControlMixin
from riclibre.helpers.model_watcher import WatchedModel
from riclibre.helpers.observation_helpers import Observable, default_notify_observers

LOGGER = logging.getLogger(__name__)

DEFAULT_VOTE_CHOICES = ['Oui', 'Non', 'Vote blanc']


class Referendum(Observable, FieldUpdateControlMixin, models.Model, metaclass=WatchedModel):
    """
    Referendum.
    """
    _observers = []
    ACHIEVEMENTS = {
        "orateur": ("orateur", "Vous avez créé puis publié un référendum.", "has_published"),
        "politicien": ("politicien", "Vous avez planifié un référendum.", "has_planned")
    }
    DURATION_CHOICES = (
        (86399, '24h'),
    )

    VALIDATION_MESSAGES = {
        "pub_gte_start": """La date de vote doit être fixée au minimum %s jours après la date de publication du 
        référendum ou après la date du jour si le référendum est déjà publié.""",
        "pub_undefined": """La date de vote ne peut être définie si le référendum n'a pas de date de publication."""
    }

    title = models.CharField(verbose_name="Titre du référendum", max_length=300, unique=True, blank=False, null=False)
    description = models.TextField(verbose_name="Description du référendum", max_length=10000)
    question = models.CharField(verbose_name="Question posée aux citoyens", max_length=300)
    categories = models.ManyToManyField("Category")
    creation_date = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)
    last_update = models.DateTimeField(verbose_name="Date de la dernière modification", auto_now=True)
    publication_date = models.DateTimeField(verbose_name="Date de publication", blank=True, null=True)
    event_start = models.DateTimeField(verbose_name="Début des votes", blank=True, null=True)
    duration = models.IntegerField(verbose_name="Durée des votes", choices=DURATION_CHOICES,
                                   default=DURATION_CHOICES[0][0])
    creator = models.ForeignKey(get_user_model(), verbose_name="Créateur", on_delete=CASCADE)
    slug = models.SlugField(max_length=300, null=True, blank=True)

    __control_fields = ["publication_date", "event_start", "duration"]

    class Meta:
        verbose_name = "Référendum"
        verbose_name_plural = "Référendums"
        ordering = ('publication_date',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Define a referendum instance url
        :return:
        """
        return reverse('referendum', kwargs={'slug': self.slug})

    def get_updatable_fields(self):
        """
        Define a list that can be updated on referendum according to its status.
        :return:
        """
        fields = ["title", "description", "question", "categories", "publication_date"]
        if self.is_published:
            fields = ["event_start", ]
        if self.is_in_progress or self.is_over:
            fields = []
        return fields

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        control_fields = self.__control_fields
        message = None

        self.update_control_fields(*control_fields)
        if self.pk and self.__was_published_before_update:
            update_fields = ['last_update', 'event_start', 'duration']
            message = "Referendum already published. Updating only allowed fields: last_update, event_start, event_end"
            control_fields = ['event_start', 'duration']

        if self.pk and (self.__was_in_progress_before_update or self.__was_over_before_update):
            update_fields = []
            message = "Referendum is in progress or is over . You can't update it."
            control_fields = []

        # define slug
        if not self.slug:
            if isinstance(update_fields, list):
                update_fields.append('slug')

            self.slug = slugify(self.title)

        if message:
            LOGGER.warning(message)
        super(Referendum, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                     update_fields=update_fields)
        self.update_control_fields(*control_fields)

    def clean(self):
        """Override clean method"""
        if not self.publication_date and self.event_start:
            raise ValidationError({"event_start": self.VALIDATION_MESSAGES['pub_undefined']})

        if not self.respect_event_start_delay():
            raise ValidationError(
                {"event_start": self.VALIDATION_MESSAGES['pub_gte_start'] % self.get_min_delay_before_event_start()})

    @staticmethod
    def get_min_delay_before_event_start():
        """
        Get minimum number of days between referendum publication and event start.
        :return: a nb of days.
        """
        nb_days = 15
        if hasattr(settings, 'NB_DAYS_BEFORE_EVENT_START'):
            nb_days = settings.NB_DAYS_BEFORE_EVENT_START
        return nb_days

    @property
    def minimum_event_start_date(self):
        """
        Compute minimum event start date.
        :return: minimum event start date.
        """
        origin_date = timezone.now()
        if self.publication_date and not self.is_published:
            origin_date = self.publication_date
        return origin_date + timezone.timedelta(days=self.get_min_delay_before_event_start())

    def respect_event_start_delay(self):
        """
        Check if number of days between publication and event start respect the minimum number of days defined in
        settings
        :return: a boolean
        """
        if self.publication_date and self.event_start:
            return self.event_start >= self.minimum_event_start_date
        return True

    @staticmethod
    def date_passed(timezone_instance):
        """
        Control if a date is previous to now()
        :param timezone_instance: a django timezone instance
        :return:
        """
        return timezone_instance < timezone.now() if timezone_instance else False

    def from_field_date_passed(self, field_name):
        """
        Control if a field date value is previous to now()
        :param field_name: a referendum field name
        :return:
        """
        original_field_name = "__original_%s" % field_name
        return self.date_passed(getattr(self, original_field_name)) if getattr(self, original_field_name) else False

    @property
    def __was_published_before_update(self):
        """
        Indicates if referendum was published before instance update.
        :return: True or False
        """

        return self.from_field_date_passed("publication_date")

    @property
    def __was_in_progress_before_update(self):
        """
        Indicates if referendum was in progress before instance update.
        :return: True or False
        """
        return self.from_field_date_passed("event_start") and not self.__was_over_before_update

    @property
    def __was_over_before_update(self):
        """
        Indicates if referendum is over.
        :return: True or False
        """

        return self.date_passed(self.__event_end)

    @property
    def __event_end(self):
        """
        Get referendum's vote end according to event start and duration.
        :return:
        """

        return getattr(self, "__original_event_start") + timezone.timedelta(
            seconds=getattr(self, "__original_duration")) if getattr(self, "__original_event_start") else None

    @property
    def event_end(self):
        """
        Get referendum's vote end according to event start and duration.
        :return:
        """
        return self.event_start + timezone.timedelta(seconds=self.duration) if self.event_start else None

    @property
    def is_published(self):
        """
        Indicates if referendum is published.
        :return: True or False
        """
        return self.publication_date < timezone.now() if self.publication_date else False

    @property
    def is_in_progress(self):
        """
        Indicates if referendum is in progress.
        :return: True or False
        """
        return self.event_start < timezone.now() < self.event_end if self.event_start and self.event_end else False

    @property
    def is_over(self):
        """
        Indicates if referendum is over.
        :return: True or False
        """
        return self.event_end < timezone.now() if self.event_end else False

    @property
    def nb_votes(self):
        """
        The number of votes for this referendum.
        :return: a number of votes
        """
        nb_votes_list = [choice.nb_votes for choice in self.choice_set.all() if choice]
        if nb_votes_list:
            return reduce(lambda a, b: a + b, nb_votes_list)
        return 0

    def get_results(self):
        """
        Get referendum results
        :return:
        """
        return self.choice_set.all()

    def has_published(self):
        """
        Grant "orateur" achievement
        :return: A boolean
        """
        return True if self.publication_date else False, self.creator

    def has_planned(self):
        """
        Grant "politicien" achievement
        :return: A boolean
        """
        return True if self.event_start else False, self.creator


class Category(models.Model):
    """
    Category is used to describe and organise referendums.
    """
    title = models.CharField(verbose_name="Titre de la catégorie", max_length=150, unique=True)
    slug = models.SlugField(max_length=300, null=True, blank=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.title)
        return super().save(force_insert=force_insert, force_update=force_update, using=using,
                            update_fields=update_fields)


class Choice(models.Model):
    """
    Choice is one option that a citizen can vote for a given referendum.
    """
    referendum = models.ForeignKey("Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Libellé du choix", max_length=150)

    class Meta:
        verbose_name = "Choix"
        verbose_name_plural = "Choix"
        constraints = [
            models.UniqueConstraint(fields=['title', 'referendum'], name='unique_choice')
        ]

    def __str__(self):
        return f"{self.referendum}:{self.title} - {self.nb_votes} soit {self.votes_percentage}% des voix"

    @classmethod
    def create_default_choices(cls, referendum):
        """
        Create default choices for a given referendum
        :param referendum: a Referendum instance
        """
        for vote_choice in DEFAULT_VOTE_CHOICES:
            with transaction.atomic():
                try:
                    Choice.objects.create(title=vote_choice, referendum=referendum)
                except IntegrityError as integiry_error:
                    LOGGER.warning(integiry_error)
                    pass

    @property
    def nb_votes(self):
        """
        The number of votes for this choice.
        :return: a number of votes
        """
        return self.vote_set.count()

    @property
    def votes_percentage(self):
        """
        The percentage of votes for this choice.
        :return: percentage of votes.
        """
        percentage = 0
        if self.referendum.nb_votes:
            percentage = (self.nb_votes / self.referendum.nb_votes) * 100
        return percentage

    def votes_percentage_html(self):
        """
        The percentage of votes for this choice formated for html
        :return: percentage of votes a html string.
        """
        return str(self.votes_percentage).replace(",", ".")


def referendum_post_save(sender, instance, **kwargs):
    """
    Launch after Referendum instance save.
    :param sender:
    :param kwargs:
    :return:
    """
    Choice.create_default_choices(referendum=instance)


post_save.connect(referendum_post_save, sender=Referendum)
post_save.connect(default_notify_observers, sender=Referendum)