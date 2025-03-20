from django.apps import AppConfig


class BtcoinsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'btcoins'

    def ready(self):
        import btcoins.signals