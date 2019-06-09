"""
Referendum's app :  Like's models
"""
import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save

from riclibre.helpers.model_watcher import WatchedModel
from riclibre.helpers.observation_helpers import Observable, default_notify_observers

LOGGER = logging.getLogger(__name__)


class Like(Observable, models.Model, metaclass=WatchedModel):
    """
    A testimony of interest from a citizen.
    """
    _observers = []
    ACHIEVEMENTS = {
        "sympathisant": ("sympathisant", "Vous avez liké un référendum.", "has_liked")
    }

    referendum = models.ForeignKey("referendum.Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = (('referendum', 'user'),)

    def __str__(self):
        return f"{self.user} s'intéresse au référendum: {self.referendum}."

    def has_liked(self):
        """
        Grant "sympathisant" success
        :return: A boolean
        """
        return bool(self.pk), self.user


post_save.connect(default_notify_observers, sender=Like)
