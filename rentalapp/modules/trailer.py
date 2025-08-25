# rentalapp/modules/trailer.py
import platform
import subprocess

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from rentalapp.forms import TrailerForm
from rentalapp.models import Trailer, ServiceHistory, TrailerLog


class TrailerViews:
    @staticmethod
    def is_trailer_active(ip_address: str) -> bool:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", ip_address]
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def trailer_list(request):
        trailers = Trailer.objects.all()
        return render(request, "rentalapp/trailer/trailer_list.html", {"trailers": trailers})

    @staticmethod
    def trailer_detail(request, pk: int):
        trailer = get_object_or_404(Trailer, pk=pk)
        service_histories = ServiceHistory.objects.filter(trailer=trailer)

        if trailer.status == "maintenance":
            active_status = "maintenance"
        else:
            active_status = "active" if TrailerViews.is_trailer_active(trailer.ip_address) else "inactive"

        return render(
            request,
            "rentalapp/trailer/trailer_detail.html",
            {
                "trailer": trailer,
                "service_histories": service_histories,
                "active_status": active_status,
            },
        )

    @staticmethod
    def trailer_create(request):
        if request.method == "POST":
            form = TrailerForm(request.POST)
            if form.is_valid():
                trailer = form.save()
                TrailerLog.objects.create(
                    trailer=trailer,
                    event_type="added",
                    message=f"Przyczepka dodana przez {request.user.username}.",
                )
                messages.success(request, f"Przyczepka '{trailer.name}' została dodana.")
                return redirect("rentalapp:trailer_detail", pk=trailer.pk)
        else:
            form = TrailerForm()

        return render(request, "rentalapp/trailer/trailer_create.html", {"form": form})

    @staticmethod
    def trailer_edit(request, pk: int):
        trailer = get_object_or_404(Trailer, pk=pk)
        old_status = trailer.status

        if request.method == "POST":
            form = TrailerForm(request.POST, instance=trailer)
            if form.is_valid():
                trailer = form.save()
                TrailerLog.objects.create(
                    trailer=trailer,
                    event_type="edited",
                    message=f"Przyczepka edytowana przez {request.user.username}.",
                )
                new_status = trailer.status
                if old_status != new_status:
                    current_time = timezone.now().strftime("%H:%M")
                    if new_status == "maintenance":
                        message_text = f"Status zmieniony na 'W serwisie' przez {request.user.username} o {current_time}"
                    else:
                        message_text = f"Status zmieniony na '{trailer.get_status_display()}' o {current_time}"
                    TrailerLog.objects.create(
                        trailer=trailer,
                        event_type="status_change",
                        message=message_text,
                    )
                messages.info(request, f"Przyczepka '{trailer.name}' została zaktualizowana.")
                return redirect("rentalapp:trailer_detail", pk=trailer.pk)
            else:
                print(form.errors)
        else:
            form = TrailerForm(instance=trailer)

        return render(request, "rentalapp/trailer/trailer_edit.html", {"form": form, "trailer": trailer})

    @staticmethod
    def trailer_delete(request, pk: int):
        trailer = get_object_or_404(Trailer, pk=pk)

        if request.method == "POST":
            trailer_name = trailer.name

            TrailerLog.objects.create(
                trailer=trailer,
                event_type="deleted",
                message=f"Przyczepka '{trailer_name}' została usunięta przez {request.user.username}",
            )

            trailer.delete()
            messages.success(request, f"Przyczepka '{trailer_name}' została usunięta.")
            return redirect("rentalapp:trailer_list")

        return redirect("rentalapp:trailer_detail", pk=pk)
