"""
Id_card_checker's app:  IdCard's models
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CASCADE
from django.db.models.signals import post_save
from django.utils import timezone

from riclibre.helpers.observation_helpers import Observable

LOGGER = logging.getLogger(__name__)


def notify_observers(sender, instance, created, **kwargs):
    """A notifying signal function"""
    if created:
        instance.process_id_card()


class IdCard(Observable, models.Model):
    """
    Represents an uploaded IDCard.
    """
    STATUS = [
        ("wait", "En attente de traitement"),
        ("failed", "Échec du traitement"),
        ("success", "Réussite du traitement")
    ]

    document = models.FileField(verbose_name="copie de la pièce d'identité", upload_to='temp_docs')
    user = models.ForeignKey(get_user_model(), verbose_name="Utilisateur associé", on_delete=CASCADE)
    status = models.CharField(verbose_name="statut du traitement", choices=STATUS, max_length=300, default=STATUS[0])
    creation = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)
    update = models.DateTimeField(verbose_name="Date de mise à jour", auto_now=True)

    def __str__(self):
        return f"{self.user} : {self.document} : {self.status}"

    @staticmethod
    def get_expiration_date(creation_date: timezone.datetime):
        """
        Compute an expiration date for id card according to creation date and validity rules.
        :param creation_date:
        :return:
        """
        try:
            if settings.ID_CARD_VALIDITY_LENGTH:
                return creation_date + timezone.timedelta(days=settings.ID_CARD_VALIDITY_LENGTH)
        except AttributeError as no_id_card_validity_setting:
            print(no_id_card_validity_setting)
            LOGGER.warning(
                "No ID_CARD_VALIDITY_LENGTH defined in project's settings %s " % no_id_card_validity_setting)
        return creation_date + timezone.timedelta(minutes=1)

    def process_id_card(self):
        """
        Add a job check identity card job to tasks.
        """
        from id_card_checker.tasks import add_check_job
        LOGGER.info('Sending new id card checking job !')
        add_check_job.delay(self.pk)

    def check_mrz(self):
        """
        Check mrz validity by analyzing document and return a boolean and a document creation date.
        :return: a boolean for validity and a creation date
        """
        # TODO : Implement check mrz
        return NotImplemented, timezone.now()

    def set_document_validity(self):
        """
        Set document validity and update instance status according to check results.
        :return: a boolean results
        """
        if self.document and self.status == "wait":
            self.change_status('failed')
            document_validity, creation_date = self.check_mrz()
            if document_validity:
                self.change_status('success')
                self.notify(valid_until=self.get_expiration_date(creation_date))
        if self.status == 'success':
            return True
        return False

    def change_status(self, status):
        """
        Method in charge of updating instance status.
        :param status: new status
        """
        self.status = status
        self.save()


post_save.connect(notify_observers, sender=IdCard)
