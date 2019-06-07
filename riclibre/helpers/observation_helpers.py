"""
This module intends to provide abstract classes that help setting observer/observable relation between apps.
"""
import logging
from importlib import import_module

from django.conf import settings

LOGGER = logging.getLogger(__name__)


def parse_observable_info(observable_name):
    """
    Parse a OBSERVATIONS_LINKS's settings formatted observable name to return its app_name and model_name
    :return: app_name, model_name
    """
    split_observable_name = observable_name.split('.')
    return split_observable_name[0], split_observable_name[-1]


def parse_observer_info(observer_full_name):
    """
    Parse a OBSERVATIONS_LINKS's settings formatted observer name to return its module_name and attribute_name
    :return: module_name, attribute_name
    """
    split_observer_name = observer_full_name.split('.')
    return '.'.join(split_observer_name[:-1]), split_observer_name[-1]


def register_observation_links(app_config_instance):
    """
    Help an app to register its observation links. To use in app's config's custom ready method.
    :param app_config_instance: an app's config instance.
    """
    for observable_name, observers in settings.OBSERVATIONS_LINKS.items():
        app_name, model_name = parse_observable_info(observable_name)
        if app_name == app_config_instance.name:
            try:
                observable = app_config_instance.get_model(model_name)
                for observer_full_name in observers:
                    module_name, attribute_name = parse_observer_info(observer_full_name)
                    observer = getattr(import_module(module_name), attribute_name)
                    observable.register_observer(observer)
                    LOGGER.info(f"Registered observation link: {observable} is now observed by {observer}.")
            except LookupError as lookup:
                LOGGER.error(lookup)


class Observer:
    """
    An abstract class to inherit from that transform an object to an observer.
    """

    def update(self, observable: 'Observable', *args, **kwargs) -> None:
        """
        Get update information from observable.
        """
        pass


class Observable:
    """
    An abstract class to inherit from that transform an object to an observable.
    """

    # _observers = []

    @classmethod
    def register_observer(cls, observer: Observer) -> None:
        """
        Add an observer to observers list.
        """
        cls._observers.append(observer)

    @classmethod
    def unregister_observer(cls, observer: Observer) -> None:
        """
        Remove an observer from observers list.
        """
        cls._observers.remove(observer)

    def notify(self, *args, **kwargs) -> None:
        """
        Notify all observer that something changed.
        """
        for observer in self._observers:
            observer.update(self, *args, **kwargs)


# default notifiying signal
def default_notify_observers(sender, instance, created, **kwargs):
    """A notifying signal function"""
    instance.notify()
