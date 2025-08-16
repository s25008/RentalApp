from celery import shared_task
from .utils import update_trailer_status

@shared_task
def ping_trailers():
    update_trailer_status()
