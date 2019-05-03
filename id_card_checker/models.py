"""
Id_card_checker's app:  IdCard's models
"""
import logging
from tkinter.constants import CASCADE

from django.contrib.auth import get_user_model
from django.db import models

LOGGER = logging.getLogger(__name__)

STATUS = [
    ("wait", "En attente de traitement"),
    ("failed", "Échec du traitement")
]


class IdCard(models.Model):
    """
    Represents an uploaded IDCard.
    """
    document = models.FileField(verbose_name="copie de la pièce d'identité", upload_to='temp_docs')
    user = models.ForeignKey(get_user_model(), verbose_name="Utilisateur associé", on_delete=CASCADE)
    status = models.CharField(verbose_name="statut du traitement", choices=STATUS, max_length=300, default=STATUS[0])
    creation = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)
    update = models.DateTimeField(verbose_name="Date de mise à jour", auto_now=True)

    def __str__(self):
        return f"{self.user} : {self.document} : {self.status}"
