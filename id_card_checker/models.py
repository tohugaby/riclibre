"""
Id_card_checker's app:  IdCard's models
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.db.models import CASCADE
from django.db.models.signals import post_save
from django.template.defaultfilters import date
from django.utils import timezone
from passporteye import read_mrz

from id_card_checker.helpers.mrz_check import check_french_mrz, split_mrz, french_structure
from riclibre.helpers.observation_helpers import Observable

LOGGER = logging.getLogger(__name__)


def notify_observers(sender, instance, created, **kwargs):
    """A notifying signal function"""
    if created and instance.document:
        instance.process_id_card()
    if created and not instance.document:
        instance.comment = "Aucun fichier soumis"
        instance.status = IdCard.FAILED
        instance.save()


class IdCard(Observable, models.Model):
    """
    Represents an uploaded IDCard.
    """
    WAIT = "wait"
    FAILED = "failed"
    SUCCESS = "success"
    STATUS = [
        (WAIT, "En attente de traitement"),
        (FAILED, "Échec du traitement"),
        (SUCCESS, "Réussite du traitement")
    ]

    document = models.ImageField(verbose_name="copie de la pièce d'identité", upload_to='temp_docs', blank=True)
    user = models.ForeignKey(get_user_model(), verbose_name="Utilisateur associé", on_delete=CASCADE)
    status = models.CharField(verbose_name="statut du traitement", choices=STATUS, max_length=300, default=WAIT)
    creation = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)
    update = models.DateTimeField(verbose_name="Date de mise à jour", auto_now=True)
    comment = models.CharField(verbose_name="Résultat détaillé de l'analyse", blank=True, max_length=2000)
    valid_until = models.DateTimeField(verbose_name='Date limite de validité', blank=True, null=True)

    class Meta:
        ordering = ['-creation', '-update']

    def __str__(self):
        return f"{self.user} : {self.document} : {self.status}"

    @property
    def is_valid_card(self):
        """
        Check if id card is valid.
        :return: A boolean that say if id card is valid
        """
        if self.valid_until:
            return self.valid_until > timezone.now()
        return False

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

    def extract_mrz(self):
        """
        Extract mrz data from document as a string
        :return: a string representation of mrz.
        """
        try:
            mrz = read_mrz(self.document.file.file, extra_cmdline_params='--oem 0', save_roi=True)
            return mrz.aux['text'].replace('\n', '')
        except AttributeError as attr_error:
            LOGGER.error("Error during idcard analysis (%s) : %s" % (self, attr_error))
            raise attr_error

    def parse_mrz(self):
        """
        Parse mrz and returns a boolean for mrz validity, a document delivery date and a comment that explains process
        results.
        :return: a boolean for mrz validity, a delivery date and a comment that explains process results.
        """
        comment = ''
        try:
            mrz_text = self.extract_mrz()
            if check_french_mrz(mrz_text):
                mrz_data = split_mrz(french_structure, mrz_text)
                delivery_date = timezone.datetime(year=int(mrz_data['delivery_year']),
                                                  month=int(mrz_data['delivery_month']), day=1)
                comment = """Votre pièce d'identité a été analysée avec succès.""".format()
                return True, delivery_date, comment
        except AttributeError as attr_error:
            comment = """ Erreur durant l'analyse de votre pièce d'identité. La cause du problème peut varier: 
            qualité du document transmis, cadrage, format du fichier... Essayer de soumettre un nouveau document."""
        except ValueError as val_error:
            comment = """ Erreur durant l'analyse de votre pièce d'identité. La cause du problème semble venir de 
            la band mrz de votre pièce d'identité... Essayer de soumettre un nouveau document."""

        return False, None, comment

    def check_document(self):
        """
        Check document validity and update instance status according to check results.
        :return: a boolean results
        """
        expiration_date = None
        if self.document and self.status == self.WAIT:
            mrz_validity, delivery_date, comment = self.parse_mrz()
            if mrz_validity:
                self.change_status(self.SUCCESS)
                expiration_date = self.get_expiration_date(delivery_date)
                self.notify(valid_until=expiration_date)

                if timezone.make_aware(expiration_date) > timezone.now():
                    formated_expiration_date = date(expiration_date, 'd/m/Y')
                    comment += f"Elle est valide jusqu'au {formated_expiration_date}"
                else:
                    comment += "Mais elle n'est plus valide"
            else:
                self.change_status(self.FAILED)
            LOGGER.info(f'Document {self.document} soumis par {self.user}:{comment}')
            self.comment = comment
            self.valid_until = expiration_date
            self.document.delete(save=True)
            self.save()
            send_mail(
                subject='R.I.C Libre : %s : Analyse de votre pièce d\'identité' % self.status,
                message=comment,
                from_email='identity.validation@riclibre.fr',
                recipient_list=[self.user.email, ])
        if self.status == self.SUCCESS:
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
