"""
Referendum's app :  Like's models
"""
import logging

from django.contrib.auth import get_user_model
from django.db import models

LOGGER = logging.getLogger(__name__)


class Like(models.Model):
    """
    A testimony of interest from a citizen.
    """
    referendum = models.ForeignKey("referendum.Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = (('referendum', 'user'),)

    def __str__(self):
        return f"{self.user} s'intéresse au référendum: {self.referendum}."
