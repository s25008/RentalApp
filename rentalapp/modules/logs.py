from django.shortcuts import render, get_object_or_404
from rentalapp.models import TrailerLog, WarehouseLog, Trailer


class LogsViews:
    @staticmethod
    def logs_view(request):
        event_type = request.GET.get('event_type')

        if event_type:
            logs = TrailerLog.objects.filter(event_type=event_type).order_by('-timestamp')
        else:
            logs = TrailerLog.objects.all().order_by('-timestamp')

        event_types = TrailerLog.objects.values_list('event_type', flat=True).distinct()

        return render(request, 'rentalapp/log.html', {
            'logs': logs,
            'event_types': event_types,
            'selected_type': event_type
        })

    @staticmethod
    def trailer_logs(request, pk):
        trailer = get_object_or_404(Trailer, pk=pk)
        trailer_logs = trailer.logs.all().order_by('-timestamp')
        return render(request, 'rentalapp/trailer/trailer_logs_partial.html', {
            'trailer': trailer,
            'trailer_logs': trailer_logs
        })

    @staticmethod
    def warehouse_logs_view(request):
        logs = WarehouseLog.objects.all().order_by('-timestamp')
        return render(request, 'rentalapp/warehouse/warehouse_logs.html', {'logs': logs})
