"""
Account manager app: App's config module
"""
from django.apps import AppConfig

from riclibre.helpers.observation_helpers import register_observation_links


class AccountManagerConfig(AppConfig):
    """
    Account manager app: App's config
    """
    name = 'account_manager'
    verbose_name = 'Gestionnaire de comptes utilisateurs'

    def ready(self):
        register_observation_links(self)
