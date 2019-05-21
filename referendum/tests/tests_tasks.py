"""
Referendum check's app: Task's tests
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models.signals import post_save, post_delete
from django.test import TestCase
from django.utils import timezone

from referendum.models import Identity, manage_citizen_perm
from referendum.tasks import remove_citizen_perm_job, clean_identities_job

LOGGER = logging.getLogger(__name__)


class TasksTestCase(TestCase):
    """
    Test tasks.
    """
    fixtures = ['test_data.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.permission = Permission.objects.get(codename='is_citizen')
        cls.permission_name = f'referendum.{cls.permission.codename}'
        cls.identity_users = get_user_model().objects.all()
        cls.non_valid_identity_date = timezone.now() - timezone.timedelta(days=5)
        cls.valid_identity_date = timezone.now() + timezone.timedelta(days=5)

    def test_remove_citizen_perm_job(self):
        """
        Test remove_citizen_perm_job
        """
        post_save.disconnect(manage_citizen_perm, sender=Identity)
        post_delete.disconnect(manage_citizen_perm, sender=Identity)
        nb_identity = Identity.objects.count()
        for user in self.identity_users:
            user.is_superuser = False
            user.save()
            user.user_permissions.add(self.permission)
            user = get_user_model().objects.get(pk=user.pk)
            self.assertTrue(user.has_perm(self.permission_name))
            Identity.objects.create(user=user, valid_until=self.non_valid_identity_date)
            user = get_user_model().objects.get(pk=user.pk)
            self.assertTrue(user.has_perm(self.permission_name))
        self.assertEqual(Identity.objects.count(), nb_identity + self.identity_users.count())
        remove_citizen_perm_job.apply()
        for user in self.identity_users:
            user = get_user_model().objects.get(pk=user.pk)
            self.assertFalse(user.has_perm(self.permission_name))

    def test_clean_identities_job(self):
        """
        Test clean_identities_job
        """
        post_save.disconnect(manage_citizen_perm, sender=Identity)
        nb_identity = Identity.objects.count()
        for user in self.identity_users:
            user.is_superuser = False
            user.save()
            user.user_permissions.add(self.permission)
            user = get_user_model().objects.get(pk=user.pk)
            self.assertTrue(user.has_perm(self.permission_name))
            Identity.objects.create(user=user, valid_until=self.non_valid_identity_date)
            user = get_user_model().objects.get(pk=user.pk)
            self.assertTrue(user.has_perm(self.permission_name))
        self.assertEqual(Identity.objects.count(), nb_identity + self.identity_users.count())
        clean_identities_job.apply()
        self.assertEqual(Identity.objects.count(), nb_identity)
        for user in self.identity_users:
            user = get_user_model().objects.get(pk=user.pk)
            self.assertFalse(user.has_perm(self.permission_name))
