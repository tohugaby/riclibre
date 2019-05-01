"""
Referendum's app: Identity's model's tests
"""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone

from referendum.models import Identity

LOGGER = logging.getLogger(__name__)


class IdentityTestCase(TestCase):
    """
    Test Identity model.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        self.permission = Permission.objects.get(codename='is_citizen')
        self.permission_name = f'referendum.{self.permission.codename}'
        self.user = get_user_model().objects.filter(is_superuser=False, is_staff=False).first()
        self.user.user_permissions.remove(self.permission)

    def test_identity_add(self):
        """
        Test that adding an Identity with valid date add citizen's permission to associated user.
        """
        self.assertFalse(self.user.has_perm(self.permission_name))
        Identity.objects.create(user=self.user, valid_until=timezone.now() + timezone.timedelta(days=2))
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(self.user.has_perm(self.permission_name))

    def test_identity_remove(self):
        """
        Test that removing an Identity with valid date remove citizen's permission to associated user.
        """
        identity = Identity.objects.create(user=self.user, valid_until=timezone.now() + timezone.timedelta(days=2))
        self.assertTrue(self.user.has_perm(self.permission_name))
        identity.delete()
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.assertFalse(self.user.has_perm(self.permission_name))

    def test_identity_add_when_another_valid_one_exists(self):
        """
        Test that adding an Identity with valid date when another valid one exists doesn't change associated user
        permissions.
        """
        Identity.objects.create(user=self.user, valid_until=timezone.now() + timezone.timedelta(days=1))
        self.assertTrue(self.user.has_perm(self.permission_name))
        Identity.objects.create(user=self.user, valid_until=timezone.now() + timezone.timedelta(days=2))
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(self.user.has_perm(self.permission_name))

    def test_validity_remove_when_another_valid_one_exists(self):
        """
        Test that removing an Identity with valid date when another valid one exists doesn't change associated user
        permissions.
        """
        Identity.objects.create(user=self.user, valid_until=timezone.now() + timezone.timedelta(days=1))
        identity = Identity.objects.create(user=self.user, valid_until=timezone.now() + timezone.timedelta(days=2))
        self.assertTrue(self.user.has_perm(self.permission_name))
        identity.delete()
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(self.user.has_perm(self.permission_name))

    def test_identity_add_when_another_invalid_one_exists(self):
        """
        Test that adding an Identity with valid date when another invalid one exists add citizen permission from
        associated user permissions.
        """
        Identity.objects.create(user=self.user, valid_until=timezone.now() - timezone.timedelta(days=1))
        self.assertFalse(self.user.has_perm(self.permission_name))
        Identity.objects.create(user=self.user, valid_until=timezone.now() + timezone.timedelta(days=2))
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(self.user.has_perm(self.permission_name))

    def test_validity_remove_when_another_invalid_one_exists(self):
        """
        Test that removing an Identity with valid date when another invalid one exists remove citizen permission from
        associated user permissions.
        """
        Identity.objects.create(user=self.user, valid_until=timezone.now() - timezone.timedelta(days=1))
        self.assertFalse(self.user.has_perm(self.permission_name))
        identity = Identity.objects.create(user=self.user, valid_until=timezone.now() + timezone.timedelta(days=2))
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(self.user.has_perm(self.permission_name))
        identity.delete()
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.assertFalse(self.user.has_perm(self.permission_name))
