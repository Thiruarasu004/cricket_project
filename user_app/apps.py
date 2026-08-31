from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user_app'

    def ready(self):
        import user_app.signals
