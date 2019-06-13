"""
Id_card_checker's app:  IdCard's models
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models, OperationalError
from django.db.models import CASCADE
from django.db.models.signals import post_save
from django.template.defaultfilters import date
from django.utils import timezone
from kombu.exceptions import OperationalError
from passporteye import read_mrz

from id_card_checker.helpers.mrz_check import check_french_mrz, split_mrz, FRENCH_STRUCTURE
from id_card_checker.validators import validate_file_size
from riclibre.helpers.model_watcher import WatchedModel
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
    instance.notify()


class IdCard(Observable, models.Model, metaclass=WatchedModel):
    """
    Represents an uploaded IDCard.
    """
    _observers = []
    ACHIEVEMENTS = {
        "citoyen": ("citoyen", "Vous avez enregistré une carte d'identité valide et obtenu le droit de vote.",
                    "is_citizen")
    }

    WAIT = "wait"
    FAILED = "failed"
    SUCCESS = "success"
    STATUS = [
        (WAIT, "En attente de traitement"),
        (FAILED, "Échec du traitement"),
        (SUCCESS, "Réussite du traitement")
    ]

    MRZ_ANALYSIS_MESSAGES = {
        "success_mrz_analysis": """Votre pièce d'identité a été analysée avec succès.""",
        "success_doc_valid": """Elle est valide jusqu'au {0}.""",
        "success_doc_expired": """Mais elle n'est plus valide""",
        "error_doc_quality": """
            Erreur d'analyse de votre pièce d'identité. Les causes possibles sont liées à la qualité du document, son
            cadrage, son format... Essayer de soumettre un nouveau document.
            """,
        "error_mrz_value": """
            Erreur d'analyse de votre pièce d'identité. Une valeur de la bande mrz est erronée...
            Essayer de soumettre un nouveau document.
            """,
        "error_mrz_structure": """
            Erreur d'analyse de votre pièce d'identité. La bande mrz est illisible ou sa structure n'est pas bonne.
            Essayer de soumettre un nouveau document.
            """,
        "error_unknown": """
            Erreur d'analyse de votre pièce d'identité. La cause de l'erreur n'est pas identifiée.
            Essayer de soumettre un nouveau document."""
    }

    document = models.ImageField(verbose_name="copie de la pièce d'identité", upload_to='temp_docs', blank=True,
                                 validators=[validate_file_size])
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
            LOGGER.warning("No ID_CARD_VALIDITY_LENGTH defined in project's settings %s ", no_id_card_validity_setting)
        return creation_date + timezone.timedelta(minutes=1)

    def process_id_card(self):
        """
        Add a job check identity card job to tasks.
        """
        from id_card_checker.tasks import add_check_job
        LOGGER.info('Sending new id card checking job !')
        try:
            add_check_job.delay(self.pk)
        except OperationalError as ope_err:
            LOGGER.error("Can't delegate the task to Celery. Check if message broker started: %s", ope_err)
            raise ope_err

    def extract_mrz(self):
        """
        Extract mrz data from document as a string
        :return: a string representation of mrz.
        """
        try:
            mrz = read_mrz(self.document.file.file, extra_cmdline_params='--oem 0', save_roi=True)
            return mrz.aux['text'].replace('\n', '')
        except AttributeError as attr_error:
            LOGGER.error("Error during idcard analysis (%s) : %s", self, attr_error)
            raise attr_error

    def parse_mrz(self):
        """
        Parse mrz and returns a boolean for mrz validity, a document delivery date and a comment that explains process
        results.
        :return: a boolean for mrz validity, a delivery date and a comment that explains process results.
        """
        mrz_is_parsed = False
        delivery_date = None
        comment = ''
        try:
            mrz_text = self.extract_mrz()
            if check_french_mrz(mrz_text):
                mrz_data = split_mrz(FRENCH_STRUCTURE, mrz_text)
                delivery_date = timezone.datetime(year=int(mrz_data['delivery_year']),
                                                  month=int(mrz_data['delivery_month']), day=1)
                mrz_is_parsed = True
                comment = self.MRZ_ANALYSIS_MESSAGES['success_mrz_analysis']
            else:
                comment = self.MRZ_ANALYSIS_MESSAGES['error_mrz_value']
        except AttributeError as attr_error:
            comment = self.MRZ_ANALYSIS_MESSAGES['error_doc_quality']
        except ValueError as val_error:
            comment = self.MRZ_ANALYSIS_MESSAGES['error_mrz_value']
        except IndexError as index_error:
            comment = self.MRZ_ANALYSIS_MESSAGES['error_mrz_structure']
        except Exception as unknown_exception:
            comment = self.MRZ_ANALYSIS_MESSAGES['error_unknown']

        return mrz_is_parsed, delivery_date, comment

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
                    comment += self.MRZ_ANALYSIS_MESSAGES['success_doc_valid'].format(formated_expiration_date)
                else:
                    comment += self.MRZ_ANALYSIS_MESSAGES['success_doc_expired']
            else:
                self.change_status(self.FAILED)
            LOGGER.info("Document %s soumis par %s: %s", self.document, self.user, comment)
            self.comment = comment
            self.valid_until = expiration_date
            self.document.delete(save=True)
            self.save()
            send_mail(
                subject='R.I.C Libre : %s : Analyse de votre pièce d\'identité' % self.status,
                message=comment,
                from_email='identity.validation@%s' % settings.MAIL_DOMAIN,
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

    def is_citizen(self):
        """
        Check if user has citizen achievements
        :return: A boolean
        """
        return self.status == self.SUCCESS, self.user


post_save.connect(notify_observers, sender=IdCard)
# post_save.connect(default_notify_observers, sender=IdCard)
