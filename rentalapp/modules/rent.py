from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from rentalapp.forms import RentalForm, CompanyForm
from rentalapp.models import Company, Rental, RentalTrailer, RentalHistory, Trailer


class RentViews:
    @staticmethod
    def company_rent_detail(request, pk):
        company = get_object_or_404(Company, pk=pk)
        rentals = Rental.objects.filter(company=company).prefetch_related('rental_trailers__trailer')

        if request.method == 'POST':
            rental_id = request.POST.get('rental_id')
            rental = get_object_or_404(Rental, id=rental_id)

            if 'remove_trailer' in request.POST:
                rt_id = request.POST.get('rental_trailer_id')
                rt = get_object_or_404(RentalTrailer, id=rt_id)
                RentalHistory.objects.create(
                    rental=rental,
                    description=f"Przyczepka {rt.trailer.name} została usunięta z wynajmu.",
                    user=request.user
                )
                rt.delete()
                messages.success(request, "Przyczepka została usunięta z wynajmu.")
                return redirect('rentalapp:company_rent_detail', pk=company.id)

            elif 'add_trailer' in request.POST:
                trailer_id = request.POST.get('trailer_id')
                collision_exists = RentalTrailer.objects.filter(
                    trailer_id=trailer_id,
                    rental__start_date__lte=rental.end_date,
                    rental__end_date__gte=rental.start_date
                ).exists()

                if collision_exists:
                    messages.error(request, "Ta przyczepka jest już przypisana do innego wynajmu w tym terminie.")
                else:
                    RentalTrailer.objects.create(rental=rental, trailer_id=trailer_id)
                    trailer = get_object_or_404(Trailer, id=trailer_id)
                    RentalHistory.objects.create(
                        rental=rental,
                        description=f"Przyczepka {trailer.name} została dodana do wynajmu.",
                        user=request.user
                    )
                    messages.success(request, "Przyczepka została dodana do wynajmu.")

                return redirect('rentalapp:company_rent_detail', pk=company.id)

            elif 'delete_rental' in request.POST:
                RentalHistory.objects.create(
                    rental=rental,
                    description=f"Wynajem został usunięty.",
                    user=request.user
                )
                rental.delete()
                messages.success(request, "Wynajem został usunięty.")
                return redirect('rentalapp:company_rent_detail', pk=company.id)

        for rental in rentals:
            overlapping = Rental.objects.filter(
                Q(start_date__lte=rental.end_date) & Q(end_date__gte=rental.start_date)
            ).exclude(id=rental.id)

            rented_ids = RentalTrailer.objects.filter(
                rental__in=overlapping
            ).values_list('trailer_id', flat=True)
            rental.available_trailers = Trailer.objects.exclude(id__in=rented_ids)

        return render(request, 'rentalapp/rent/company_rent_detail.html', {
            'company': company,
            'rentals': rentals
        })

    @staticmethod
    def add_rental(request):
        company_id = request.GET.get('company_id')

        if request.method == 'POST':
            form = RentalForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Wynajem został dodany.")
                return redirect('rentalapp:rent')
        else:
            if company_id:
                try:
                    company = Company.objects.get(id=company_id)
                    form = RentalForm(initial={'company': company})
                except Company.DoesNotExist:
                    form = RentalForm()
            else:
                form = RentalForm()

        return render(request, 'rentalapp/rent/add_rental.html', {'form': form})

    @staticmethod
    def add_company(request):
        if request.method == 'POST':
            form = CompanyForm(request.POST)
            if form.is_valid():
                company = form.save()
                messages.success(request, 'Firma została dodana.')
                return redirect(f"{reverse('rentalapp:add_rental')}?company_id={company.id}")
        else:
            form = CompanyForm()
        return render(request, 'rentalapp/rent/add_company.html', {'form': form})

    @staticmethod
    def delete_company(request, pk):
        company = get_object_or_404(Company, pk=pk)
        company.delete()
        messages.success(request, "Firma została usunięta.")
        return redirect('rentalapp:rent')

    @staticmethod
    def delete_rental(request, pk):
        rental = get_object_or_404(Rental, pk=pk)
        rental.delete()
        messages.success(request, "Wynajem został usunięty.")
        return redirect('rentalapp:rent')

    @staticmethod
    def company_list_view(request):
        companies = Company.objects.all()

        for company in companies:
            rentals = Rental.objects.filter(company=company)
            company.total_rentals = rentals.count()
            company.total_income = sum(r.cost for r in rentals)

        return render(request, 'rentalapp/rent/company_list.html', {
            'companies': companies
        })

    @staticmethod
    def rent_view(request):
        companies = Company.objects.filter(rentals__isnull=False).distinct().prefetch_related('rentals')

        for company in companies:
            company.total_cost = company.rentals.aggregate(total=Sum('cost'))['total'] or 0

        return render(request, 'rentalapp/rent/rent.html', {
            'companies': companies
        })

    @staticmethod
    def rental_history_view(request):
        rentals = Rental.objects.select_related('company').prefetch_related('rental_trailers__trailer')
        return render(request, 'rentalapp/rent/rental_history.html', {
            'rentals': rentals
        })
