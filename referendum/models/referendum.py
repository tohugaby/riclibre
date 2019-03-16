"""
Referendum's app: Referendum's models
"""

import logging
from functools import reduce

from django.db import models
from django.utils import timezone

from referendum.models.utils import FieldUpdateControlMixin

LOGGER = logging.getLogger(__name__)


class Referendum(FieldUpdateControlMixin, models.Model):
    """
    Referendum.
    """
    DURATION_CHOICES = (
        (86399, '24h'),
    )

    title = models.CharField(verbose_name="Titre du référendum", max_length=300)
    description = models.TextField(verbose_name="Description du référendum", max_length=10000)
    question = models.CharField(verbose_name="Question posée aux citoyens", max_length=300)
    categories = models.ManyToManyField("Category")
    creation_date = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)
    last_update = models.DateTimeField(verbose_name="Date de la dernière modification", auto_now=True)
    publication_date = models.DateTimeField(verbose_name="Date de publication", blank=True, null=True)
    event_start = models.DateTimeField(verbose_name="Début des votes", blank=True, null=True)
    duration = models.IntegerField(verbose_name="Durée des votes", choices=DURATION_CHOICES,
                                   default=DURATION_CHOICES[0][0])

    __control_fields = ["publication_date", "event_start", "duration"]

    class Meta:
        verbose_name = "Référendum"
        verbose_name_plural = "Référendums"

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        control_fields = self.__control_fields
        message = None

        if self.pk and self.__was_published_before_update:
            update_fields = ['last_update', 'event_start', 'duration']
            message = "Referendum already published. Updating only allowed fields: last_update, event_start, event_end"
            control_fields = ['event_start', 'duration']

        if self.pk and (self.__was_in_progress_before_update or self.__was_over_before_update):
            update_fields = []
            message = "Referendum is in progress or is over . You can't update it."
            control_fields = []

        if message:
            LOGGER.warning(message)
        super(Referendum, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                     update_fields=update_fields)
        self.update_control_fields(*control_fields)

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
        return reduce(lambda a, b: a + b, [choice.nb_votes for choice in self.choice_set.all()])

    def get_results(self):
        """
        Get referendum results
        :return:
        """
        return self.choice_set.all()


class Category(models.Model):
    """
    Category is used to describe and organise referendums.
    """
    title = models.CharField(verbose_name="Titre de la catégorie", max_length=150)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.title


class Choice(models.Model):
    """
    Choice is one option that a citizen can vote for a given referendum.
    """
    referendum = models.ForeignKey("Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Libellé du choix", max_length=150)

    class Meta:
        verbose_name = "Choix"
        verbose_name_plural = "Choix"

    def __str__(self):
        return f"{self.referendum}:{self.title} - {self.nb_votes} soit {self.votes_percentage}% des voix"

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
