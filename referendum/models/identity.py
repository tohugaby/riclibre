"""
Referendum's app:  Identity's models
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import models
from django.db.models import CASCADE
from django.db.models.signals import post_save, post_delete
from django.utils import timezone


def manage_citizen_perm(sender, instance, **kwargs):
    """
    Add citizen perm if sender is a valid identity
    :param sender: an Identity instance
    """
    permission = Permission.objects.get(codename='is_citizen')
    user = get_user_model().objects.get(pk=instance.user.pk)
    user.user_permissions.remove(permission)
    highest_validity = sender.objects.filter(user=user).order_by('-valid_until').first()
    if highest_validity and highest_validity.is_valid_identity:
        user.user_permissions.add(permission)
        user.save()


class Identity(models.Model):
    """
    A user identity.
    """
    user = models.ForeignKey(get_user_model(), verbose_name='citoyen', on_delete=CASCADE)
    valid_until = models.DateTimeField(verbose_name='Date limite de validité')
    creation = models.DateTimeField(verbose_name='Date de création', auto_now_add=True)

    class Meta:
        verbose_name = "Validité d'une identité"
        verbose_name_plural = "Validités des identités"

    def __str__(self):
        return f"{self.user} est citoyen jusqu'au {self.valid_until}"

    @property
    def is_valid_identity(self):
        """
        Check if identity is valid.
        :return: A boolean that say if identity is valid
        """
        return self.valid_until > timezone.now()


post_save.connect(manage_citizen_perm, sender=Identity)
post_delete.connect(manage_citizen_perm, sender=Identity)
