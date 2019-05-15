"""
Id Card check's app: Task's tests
"""
from django.contrib.auth import get_user_model
from django.core.files import File
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
        user = get_user_model().objects.first()
        id_card = IdCard(user=user)
        id_card_document = File(open('./id_card_checker/tests/images/specimen.jpg', 'rb'))
        id_card.document.save('specimen.jpg', id_card_document)
        result = add_check_job.apply(args=(id_card.pk,))
        self.assertTrue(result.get())
        self.assertTrue(result.successful())
