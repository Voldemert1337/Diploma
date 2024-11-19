from django.apps import AppConfig


class Task1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Task1'

    def ready(self):
        import Task1.signals
