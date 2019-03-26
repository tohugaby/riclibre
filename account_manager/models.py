"""
Account manager app: User's models module
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    A custom user model
    """
    email = models.EmailField(_('email address'), unique=True)
    last_update = models.DateTimeField(verbose_name="Dernière mise à jour", auto_now=True)
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
