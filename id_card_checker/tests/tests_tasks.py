"""
Id Card check's app: Task's tests
"""
import logging

from django.contrib.auth import get_user_model
from django.core.files import File
from django.test import TestCase

from id_card_checker.models import IdCard
from id_card_checker.tasks import add_check_job, launch_waiting_id_cards_checks

LOGGER = logging.getLogger(__name__)


class TasksTestCase(TestCase):
    """
    Test tasks.
    """
    fixtures = ['id_card_checker_test_data.json']

    def test_add_check_job(self):
        """
        test add_check_job.
        """
        user = get_user_model().objects.first()
        id_card = IdCard(user=user)
        id_card_document = File(open('./id_card_checker/tests/images/specimen.jpg', 'rb'))
        id_card.document.save('specimen.jpg', id_card_document)
        result = add_check_job.apply(args=(id_card.pk,))
        self.assertTrue(result.get())
        self.assertTrue(result.successful())

    def test_launch_waiting_id_cards_checks(self):
        """
        test launch_waiting_id_cards_checks.
        """
        user = get_user_model().objects.first()
        id_card = IdCard(user=user)
        id_card_document = File(open('./id_card_checker/tests/images/specimen.jpg', 'rb'))
        id_card.document.save('specimen.jpg', id_card_document)
        result = launch_waiting_id_cards_checks.apply()
        self.assertTrue(result.get())
        self.assertTrue(result.successful())
        id_card.refresh_from_db()
        self.assertEqual(id_card.status, IdCard.SUCCESS)
        self.assertFalse(bool(id_card.document))
