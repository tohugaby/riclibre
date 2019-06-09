"""
Id Card checker apps : tasks module
"""
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from id_card_checker.models import IdCard
from riclibre.helpers.tasks_helpers import TransactionAwareTask


@shared_task(base=TransactionAwareTask, bind=True)
def add_check_job(self, primary_key):
    """
    add a ckeck identity job to queue
    :param primary_key: Idcard primary key.
    :return:
    """
    id_card = IdCard.objects.get(pk=primary_key)
    return id_card.check_document()


@shared_task()
def launch_waiting_id_cards_checks():
    """
    Launch check job on all IdCard instances with wait status
    """
    id_cards = IdCard.objects.filter(status=IdCard.WAIT)
    for id_card in id_cards:
        return id_card.check_document()
