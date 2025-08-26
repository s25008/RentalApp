from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa

from rentalapp.models import Trailer, Rental, WarehouseItem, ServiceHistory


class ReportsViews:
    @staticmethod
    def generate_report_pdf(request):
        trailers = Trailer.objects.all()
        rentals = Rental.objects.select_related('company').all()
        warehouse_items = WarehouseItem.objects.all()
        services = ServiceHistory.objects.all()

        context = {
            'trailers': trailers,
            'rentals': rentals,
            'warehouse_items': warehouse_items,
            'services': services,
            'generated_on': timezone.now()
        }

        template = get_template("rentalapp/report_template.html")
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="raport.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Błąd podczas generowania PDF', status=500)
        return response