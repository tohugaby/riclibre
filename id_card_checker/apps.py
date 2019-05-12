import logging

from django.apps import AppConfig

from riclibre.helpers.observation_helpers import register_observation_links

LOGGER = logging.getLogger(__name__)


class IdCardCheckerConfig(AppConfig):
    name = 'id_card_checker'

    def ready(self):
        register_observation_links(self)
