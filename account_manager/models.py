"""
Account manager app: User's models module
"""
import logging

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from riclibre.helpers.model_watcher import WatchedModel
from riclibre.helpers.observation_helpers import Observable, default_notify_observers

LOGGER = logging.getLogger(__name__)


class CustomUser(Observable, AbstractUser, metaclass=WatchedModel):
    """
    A custom user model
    """
    _observers = []

    ACHIEVEMENTS = {
        "utilisateur": ("utilisateur", "Vous avez créé puis activé votre compte utilisateur.", "is_user")
    }

    email = models.EmailField(_('email address'), unique=True)
    last_update = models.DateTimeField(verbose_name="Dernière mise à jour", auto_now=True)
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def is_user(self):
        """
        Check if user is 'utilisateur'
        :return: a Boolean
        """
        return self.is_active, self


post_save.connect(default_notify_observers, sender=CustomUser)
