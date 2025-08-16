from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Trailer, TrailerLog

@receiver(post_save, sender=Trailer)
def log_trailer_save(sender, instance, created, **kwargs):
    if created:
        event_type = 'added'
        message = f"Przyczepka '{instance.name}' została dodana (ID: {instance.pk})."
    else:
        event_type = 'edited'
        message = f"Przyczepka '{instance.name}' została edytowana (ID: {instance.pk})."
    TrailerLog.objects.create(trailer=instance, event_type=event_type, message=message)

@receiver(post_delete, sender=Trailer)
def log_trailer_delete(sender, instance, **kwargs):
    TrailerLog.objects.create(
        trailer=instance,
        event_type='deleted',
        message=f"Przyczepka '{instance.name}' została usunięta (ID: {instance.pk})."
    )
