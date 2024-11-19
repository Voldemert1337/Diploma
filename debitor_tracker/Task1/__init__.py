from __future__ import absolute_import, unicode_literals
from debitor_tracker.celery import app as celery_app

default_app_config = 'Task1.apps.Task1Config'


# это позволит убедиться, что Celery настроен и обнаруживает задачи.


__all__ = ('celery_app',)
