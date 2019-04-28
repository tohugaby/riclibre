"""
This module intends to provide abstract classes that help setting observer/observable relation between apps.
"""


class Observer:
    """
    An abstract class to inherit from that transform an object to an observer.
    """

    def update(self, observable: 'Observable') -> None:
        """
        Get update information from observable.
        """
        pass


class Observable:
    """
    An abstract class to inherit from that transform an object to an observable.
    """
    _observers = []

    def register_observer(self, observer: Observer) -> None:
        """
        Add an observer to observers list.
        """
        self._observers.append(observer)

    def unregister_observer(self, observer: Observer) -> None:
        """
        Remove an observer from observers list.
        """
        self._observers.remove(observer)

    def notify(self) -> None:
        """
        Notify all observer that something changed.
        """
        for observer in self._observers:
            observer.update(self)
