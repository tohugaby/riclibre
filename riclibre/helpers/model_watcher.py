"""
An helper module to watch and register models
"""
import logging

from django.db.models.base import ModelBase

LOGGER = logging.getLogger(__name__)


class Register:
    """
    A simple register
    """
    WATCHED_MODELS = []


class WatchedModel(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        Register.WATCHED_MODELS.append((name, attrs['__module__']))
        # LOGGER.info(Register.WATCHED_MODELS)
        new = super().__new__(cls, name, bases, attrs, **kwargs)
        return new
