"""
Referendum's app : Vote's models
"""
import logging
from secrets import token_urlsafe

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save

from referendum.exceptions import UserHasAlreadyVotedError
from referendum.models.utils import FieldUpdateControlMixin
from riclibre.helpers.model_watcher import WatchedModel
from riclibre.helpers.observation_helpers import Observable, default_notify_observers

LOGGER = logging.getLogger(__name__)


class Vote(FieldUpdateControlMixin, models.Model):
    """
    Citizen's response to a referendum.
    """
    choice = models.ForeignKey("referendum.Choice", verbose_name="Valeur du vote", on_delete=models.CASCADE)
    vote_date = models.DateTimeField(verbose_name="Date de vote", auto_now_add=True)

    __control_fields = ["choice_id", "vote_date"]

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"

    def __str__(self):
        return f"{self.choice} - {self.vote_date}"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        control_fields = self.__control_fields
        message = None
        if self.pk:
            message = "Can't change a vote."
            control_fields = []
            update_fields = []

        if message:
            LOGGER.warning(message)
        super(Vote, self).save(force_insert=force_insert, force_update=force_update, using=using,
                               update_fields=update_fields)
        self.update_control_fields(*control_fields)

    @property
    def referendum(self):
        """
        Get referendum from choice.
        :return:
        """
        return self.choice.referendum


class VoteToken(Observable, FieldUpdateControlMixin, models.Model, metaclass=WatchedModel):
    """
    One instance of VoteToken is a single-use voter card.
    """
    _observers = []
    ACHIEVEMENTS = {
        "votant": ("votant", "Vous avez voté au moins une fois.", "has_voted")
    }

    referendum = models.ForeignKey("referendum.Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)
    token = models.CharField(verbose_name="Token", max_length=50, unique=True)
    voted = models.BooleanField(verbose_name="A voté ?", default=False)

    __control_fields = ["voted"]

    class Meta:
        verbose_name = "Token de vote"
        verbose_name_plural = "Tokens de vote"
        unique_together = (('referendum', 'user'),)
        permissions = (
            ("is_citizen", "Has citizen status"),
        )

    def __str__(self):
        return "{}: L'utilisateur {} {} en utilisant le token {}".format(
            self.referendum,
            self.user,
            "a voté" if self.voted else "n'a pas voté",
            self.token)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        control_fields = self.__control_fields
        message = None

        self.update_control_fields(*control_fields)
        if self.pk:
            update_fields = ['voted']
            if getattr(self, "__original_voted") is True:
                self.voted = True
                message = "Can't change VoteToken instance's \"voted\" field because attached user already votes"
                update_fields = []
                control_fields = []
        else:
            self.token = self.generate_token()

        if message:
            LOGGER.warning(message)
        super(VoteToken, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                    update_fields=update_fields)

        self.update_control_fields(*control_fields)

    @classmethod
    def generate_token(cls):
        """
        generate a unique token
        :return:
        """
        token = ""
        while not token or token in cls.objects.all().values('token'):
            token = token_urlsafe(30)
        return token

    def vote(self, choice):
        """
        register a vote
        :return:
        """
        if not self.voted:
            new_vote = Vote(choice=choice)
            new_vote.save()
            self.voted = True
            self.save()
            # return new_vote
        else:
            raise UserHasAlreadyVotedError

    def has_voted(self):
        """
        Grant "Votant" success
        :return: A boolean
        """
        return self.voted, self.user


post_save.connect(default_notify_observers, sender=VoteToken)
