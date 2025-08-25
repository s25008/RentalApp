from django.shortcuts import render
from rentalapp.models import Trailer


class MapViews:
    @staticmethod
    def map_view(request):
        trailers = Trailer.objects.exclude(latitude=None).exclude(longitude=None).values('name', 'latitude', 'longitude')
        total_trailers = Trailer.objects.count()

        context = {
            'trailers_json': list(trailers),
            'total_trailers': total_trailers
        }
        return render(request, 'rentalapp/map_leaflet.html', context)
