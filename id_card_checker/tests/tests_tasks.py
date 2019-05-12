"""
Id Card check's app: Task's tests
"""
from django.test import TestCase

from id_card_checker.models import IdCard
from id_card_checker.tasks import add_check_job


class TasksTestCase(TestCase):
    """
    Test tasks.
    """
    fixtures = ['id_card_checker_test_data.json']

    def test_add_check_job(self):
        """
        test add_check_job.
        """
        id_card = IdCard.objects.first()
        result = add_check_job.apply(args=(id_card.pk,))
        self.assertTrue(result.get())
        self.assertTrue(result.successful())
