from django.apps import AppConfig


class GeographyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'geography'
    
    def ready(self):
        import geography.signals