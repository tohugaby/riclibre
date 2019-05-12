"""
Id Card check's app: IdCard's model's tests
"""
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone

from id_card_checker.models import IdCard


class IdCardTestCase(TestCase):
    """
    Test IdCard model and its methods.
    """

    def test_expiration_date_calculation(self):
        """
        test expiration date computing method.
        """

        validity_length = settings.ID_CARD_VALIDITY_LENGTH
        creation_date = timezone.now()
        self.assertTrue(validity_length)
        self.assertEqual(IdCard.get_expiration_date(creation_date),
                         creation_date + timezone.timedelta(days=validity_length))

    @override_settings()
    def test_expiration_date_calculation_when_no_id_card_validity_setting_exists(self):
        """
        test expiration date computing method.
        """
        del settings.ID_CARD_VALIDITY_LENGTH
        with self.assertRaises(AttributeError):
            validity_length = settings.ID_CARD_VALIDITY_LENGTH
        creation_date = timezone.now()
        self.assertEqual(IdCard.get_expiration_date(creation_date), creation_date + timezone.timedelta(minutes=1))
