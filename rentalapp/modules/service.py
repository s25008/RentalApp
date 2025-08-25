from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from rentalapp.constants import SERVICE_CENTER
from rentalapp.models import Trailer, ServiceHistory, TrailerLog, RentalTrailer


class ServiceViews:
    @staticmethod
    def servicehistory_list(request):
        service_histories = ServiceHistory.objects.select_related('trailer').all()
        return render(
            request,
            'rentalapp/service/servicehistory_list.html',
            {'service_histories': service_histories},
        )

    @staticmethod
    def service_history_view(request):
        services = ServiceHistory.objects.select_related('trailer').order_by('-service_date')
        return render(
            request,
            'rentalapp/service/servicehistory_list.html',
            {'service_histories': services},
        )

    @staticmethod
    def active_services_view(request):
        trailers_in_service = Trailer.objects.filter(status='maintenance')
        return render(
            request,
            'rentalapp/service/active_services.html',
            {'trailers': trailers_in_service},
        )

    @staticmethod
    def send_for_service(request, pk):
        trailer = get_object_or_404(Trailer, pk=pk)

        if request.method == 'POST':
            status = request.POST.get('status')
            service_type = request.POST.get('service_type')
            note = request.POST.get('note')

            trailer.status = status
            trailer.notes = note

            trailer.latitude = SERVICE_CENTER["lat"]
            trailer.longitude = SERVICE_CENTER["lon"]

            trailer.save(update_fields=['status', 'notes', 'latitude', 'longitude'])

            TrailerLog.objects.create(
                trailer=trailer,
                event_type='status_change',
                message=f"Przyczepka wysłana na serwis ({service_type}) - {note}. "
                        f"Lokalizacja: {SERVICE_CENTER['name']}, {SERVICE_CENTER['address']}",
            )

            ServiceHistory.objects.create(
                trailer=trailer,
                service_date=timezone.now().date(),
                description=f"{service_type} - {note} (lokalizacja: {SERVICE_CENTER['name']})",
                cost=0,
            )

            if service_type and service_type.lower() == 'transport':
                RentalTrailer.objects.filter(trailer=trailer).delete()
                messages.info(
                    request,
                    f"Przyczepka {trailer.name} została usunięta z wynajmów i wysłana na transport "
                    f"do: {SERVICE_CENTER['name']}."
                )
            else:
                messages.success(
                    request,
                    f"Przyczepka {trailer.name} została wysłana na serwis do: {SERVICE_CENTER['name']}."
                )

            return redirect('rentalapp:trailer_detail', pk=pk)

        return render(request, 'rentalapp/service/send_for_service.html', {'trailer': trailer})

    @staticmethod
    def mark_service_done(request, pk):
        trailer = get_object_or_404(Trailer, pk=pk)

        if request.method == 'POST':
            comment = request.POST.get('comment', '').strip()

            ServiceHistory.objects.create(
                trailer=trailer,
                service_date=timezone.now().date(),
                description=comment or "Serwis zakończony bez opisu.",
                cost=0,
            )

            trailer.status = 'inactive'
            trailer.save()

            TrailerLog.objects.create(
                trailer=trailer,
                event_type='status_change',
                message=f"Przyczepka {trailer.name} zakończyła serwis. Notatka: {comment}",
            )

            messages.success(request, f"Przyczepka {trailer.name} zakończyła serwis.")
            return redirect('rentalapp:service_history_view')

        return render(request, 'rentalapp/service/mark_service_done.html', {'trailer': trailer})
