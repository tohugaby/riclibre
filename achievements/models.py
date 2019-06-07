"""
Achievement's app: Models
"""
from django.contrib.auth import get_user_model
from django.db import models

from achievements.helpers.badges import BADGES


class Achievement(models.Model):
    """
    Represent a use achievement.
    """
    creation_date = models.DateTimeField(verbose_name="Date d'obtention du badge", auto_now_add=True)
    user = models.ForeignKey(get_user_model(), verbose_name="Utilisateur", on_delete=models.CASCADE)
    badge = models.CharField(verbose_name="Badge obtenu", max_length=50, choices=BADGES)

    class Meta:
        verbose_name = "Succès"
        verbose_name_plural = "Succès"
        constraints = [
            models.UniqueConstraint(fields=["user", "badge"], name="user_badge_unique")
        ]

    def __str__(self):
        """
        Achievement representation
        """
        return "%s:%s" % (self.user, self.badge)
