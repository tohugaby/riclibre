from __future__ import absolute_import, unicode_literals

from .celery import app as celery_app

__version__ = "1.1.0"

__all__ = ('celery_app')
