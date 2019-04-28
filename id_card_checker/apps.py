from queue import Queue

from django.apps import AppConfig

JOB_QUEUE = Queue()


class IdCardCheckerConfig(AppConfig):
    name = 'id_card_checker'
