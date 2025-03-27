from django.apps import AppConfig

class CourierConfig(AppConfig):
    name = 'courier'

    def ready(self):
        import courier.signals