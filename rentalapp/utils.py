import os
import subprocess
import threading
import time
from .models import Trailer

def ping_trailer(ip):
    """Sprawdza, czy przyczepka odpowiada na ping"""
    try:
        output = subprocess.run(
            ["ping", "-n", "1", ip] if os.name == "nt" else ["ping", "-c", "1", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2
        )
        return output.returncode == 0
    except Exception:
        return False

def update_trailer_status():
    """Sprawdza status każdej przyczepki i aktualizuje go w bazie"""
    while True:
        print("Sprawdzanie statusu przyczepek...")

        trailers = Trailer.objects.all()
        for trailer in trailers:
            if trailer.status == "maintenance":
                continue

            is_active = ping_trailer(trailer.ip_address)

            if is_active:
                trailer.status = "active"
            else:
                trailer.status = "inactive"

            trailer.save()

        print("Statusy zaktualizowane. Kolejna aktualizacja za 5 minut...")
        time.sleep(300000)
