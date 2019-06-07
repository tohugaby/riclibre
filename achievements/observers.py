"""
Achievements app : Observer module
"""
import logging

from django.db import IntegrityError, transaction

from achievements.models import Achievement
from riclibre.helpers.observation_helpers import Observer

LOGGER = logging.getLogger(__name__)


class AchievementsObserver(Observer):
    """
    Observes models that provides achievements.
    """

    def update(self, observable: 'Observable',*args,**kwargs) -> None:
        """
        Get update information from observable.
        """
        if hasattr(observable, 'ACHIEVEMENTS'):
            for key, check in observable.ACHIEVEMENTS.items():
                badge = key
                achieved, user = getattr(observable, check[2])()
                if achieved:
                    try:
                        with transaction.atomic():
                            Achievement.objects.create(user=user, badge=badge)
                    except IntegrityError as unique_constraint:
                        LOGGER.info("User %s still got '%s' badge." % (user, badge))


achievements_observer = AchievementsObserver()
