"""
Id Card check's app: IdCard's model's tests
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files import File
from django.test import TestCase, override_settings
from django.utils import timezone

from id_card_checker.models import IdCard


class IdCardTestCase(TestCase):
    """
    Test IdCard model and its methods.
    """
    fixtures = ['id_card_checker_test_data.json']

    def test_expiration_date_calculation(self):
        """
        Test expiration date computing method.
        """

        validity_length = settings.ID_CARD_VALIDITY_LENGTH
        creation_date = timezone.now()
        self.assertTrue(validity_length)
        self.assertEqual(IdCard.get_expiration_date(creation_date),
                         creation_date + timezone.timedelta(days=validity_length))

    @override_settings()
    def test_expiration_date_calculation_when_no_id_card_validity_setting_exists(self):
        """
        Test expiration date computing method.
        """
        del settings.ID_CARD_VALIDITY_LENGTH
        with self.assertRaises(AttributeError):
            validity_length = settings.ID_CARD_VALIDITY_LENGTH
        creation_date = timezone.now()
        self.assertEqual(IdCard.get_expiration_date(creation_date), creation_date + timezone.timedelta(minutes=1))

    def test_parse_mrz(self):
        """
        Test parse_mrz method returns a tuple (True,delivery_date,comment) when image can be analysed.
        """
        user = get_user_model().objects.first()
        id_card = IdCard(user=user)
        id_card_document = File(open('./id_card_checker/tests/images/specimen.jpg', 'rb'))
        id_card.document.save('specimen.jpg', id_card_document)
        result, delivery_date, comment = id_card.parse_mrz()
        self.assertTrue(result)
        self.assertEqual(delivery_date, timezone.datetime(year=1988, month=6, day=1))
        self.assertNotEqual(comment, '')

    def test_check_mrz_failed_image_analysis(self):
        """
        Test parse_mrz method returns a tuple (False, None,comment) when image can't be analysed.
        """
        user = get_user_model().objects.first()
        id_card = IdCard(user=user)
        id_card_document = File(open('./id_card_checker/tests/images/specimen_2.jpg', 'rb'))
        id_card.document.save('specimen.jpg', id_card_document)
        result, delivery_date, comment = id_card.parse_mrz()
        self.assertFalse(result)
        self.assertEqual(delivery_date, None)
        self.assertNotEqual(comment, '')

    def test_check_document(self):
        """
        Test check_document method when image can be analysed.
        """
        self.assertEqual(len(mail.outbox), 0)
        user = get_user_model().objects.first()
        id_card = IdCard(user=user)
        id_card_document = File(open('./id_card_checker/tests/images/specimen.jpg', 'rb'))
        id_card.document.save('specimen.jpg', id_card_document)
        result = id_card.check_document()
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)

    def test_check_document_failed(self):
        """
        Test check_document method when it failed
        """
        self.assertEqual(len(mail.outbox), 0)
        user = get_user_model().objects.first()
        id_card = IdCard(user=user)
        id_card_document = File(open('./id_card_checker/tests/images/specimen_2.jpg', 'rb'))
        id_card.document.save('specimen.jpg', id_card_document)
        result = id_card.check_document()
        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 1)
