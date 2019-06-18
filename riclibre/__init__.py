"""
Riclibre project
"""
from __future__ import absolute_import, unicode_literals

from .celery import app as celery_app

__version__ = "1.5.3"

__all__ = ('celery_app')
