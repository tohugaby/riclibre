"""
Referendum's app: App's config
"""

from django.apps import AppConfig

from riclibre.helpers.observation_helpers import register_observation_links


class ReferendumConfig(AppConfig):
    """
    Referendum 's app's config.
    """
    name = 'referendum'
    verbose_name = 'Gestionnaire de référendum'

    def ready(self):
        register_observation_links(self)
