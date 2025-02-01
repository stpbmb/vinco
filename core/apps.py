from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'
    
    def ready(self):
        """
        Perform initialization tasks when the app is ready.
        This is a good place to register signals or perform other setup.
        """
        pass
