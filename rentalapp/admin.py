from django.contrib import admin
from .models import Trailer, Rental, ServiceHistory, Company, RentalTrailer

class RentalTrailerInline(admin.TabularInline):
    model = RentalTrailer
    extra = 1

class RentalAdmin(admin.ModelAdmin):
    inlines = [RentalTrailerInline]

admin.site.register(Trailer)
admin.site.register(Company)
admin.site.register(ServiceHistory)
admin.site.register(Rental, RentalAdmin)
