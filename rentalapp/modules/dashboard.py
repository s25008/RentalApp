import json
from django.shortcuts import render
from django.contrib.auth.models import User
from rentalapp.models import Trailer, WarehouseItem, Rental, RentalTrailer


class DashboardViews:
    @staticmethod
    def dashboard_view(request):
        from django.db.models.functions import TruncMonth
        from django.db.models import Count

        total_trailers = Trailer.objects.count()
        inactive_trailers = Trailer.objects.filter(status='inactive').count()
        items_below_5 = WarehouseItem.objects.filter(quantity__lt=5).count()
        total_users = User.objects.count()

        monthly_data = (
            Rental.objects
            .annotate(month=TruncMonth('start_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        months = [entry['month'].strftime('%Y-%m') for entry in monthly_data]
        rental_counts = [entry['count'] for entry in monthly_data]

        rented_trailer_ids = RentalTrailer.objects.values_list('trailer_id', flat=True).distinct()
        rented_count = Trailer.objects.filter(id__in=rented_trailer_ids).count()
        free_count = Trailer.objects.exclude(id__in=rented_trailer_ids).count()

        context = {
            'total_trailers': total_trailers,
            'inactive_trailers': inactive_trailers,
            'items_below_5': items_below_5,
            'total_users': total_users,
            'months': json.dumps(months),
            'rental_counts': json.dumps(rental_counts),
            'trailer_status_counts': json.dumps([rented_count, free_count]),
        }

        return render(request, 'rentalapp/dashboard.html', context)
