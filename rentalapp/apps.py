from django.apps import AppConfig

class RentalappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rentalapp'

    def ready(self):
        from .utils import update_trailer_status
        import threading

        thread = threading.Thread(target=update_trailer_status, daemon=True)
        thread.start()
