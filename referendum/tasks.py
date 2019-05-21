import logging

from celery import task
from django.utils import timezone

from referendum.models import Identity, manage_citizen_perm

LOGGER = logging.getLogger(__name__)


@task()
def remove_citizen_perm_job():
    """
    add a check citizen perms job to queue
    """
    identities = Identity.objects.filter(valid_until__lte=timezone.now())
    for identity in identities:
        manage_citizen_perm(Identity, identity)


@task()
def clean_identities_job():
    """
    add a identities clean job.
    """
    Identity.clean_identities()
