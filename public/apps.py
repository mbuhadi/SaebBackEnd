from django.apps import AppConfig
class PublicConfig(AppConfig):
    name = "public"

    def ready(self):
        # Sets up signal
        import public.signals
