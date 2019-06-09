"""
Id Card checker app: app config module
"""
import logging

from django.apps import AppConfig

from riclibre.helpers.observation_helpers import register_observation_links

LOGGER = logging.getLogger(__name__)


class IdCardCheckerConfig(AppConfig):
    """
    Id Card app config class
    """
    name = 'id_card_checker'
    verbose_name = "Gestionnaire de cartes d'identités"

    def ready(self):
        register_observation_links(self)
