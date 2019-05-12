from referendum.models import Identity
from riclibre.helpers.observation_helpers import Observer


class IdCheckerObserver(Observer):
    """
    Observes Id checker
    """

    def update(self, observable: 'Observable', *args, **kwargs) -> None:
        """

        :param observable:
        :return:
        """
        Identity.objects.create(user=observable.user, valid_until=kwargs['valid_until'])


id_checker_observer = IdCheckerObserver()
