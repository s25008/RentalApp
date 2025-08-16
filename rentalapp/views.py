import subprocess
import platform
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa

from .models import (
    Trailer, ServiceHistory, TrailerLog, WarehouseLog,
    Company, RentalTrailer, RentalHistory, Rental, WarehouseItem
)
from .forms import (
    TrailerForm, UserRoleForm, WarehouseItemForm,
    RentalForm, CompanyForm
)


def is_trailer_active(ip_address):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False


@login_required
def history_view(request):
    return render(request, 'rentalapp/history.html')


# Widoki dla przyczepek

@login_required
def trailer_list(request):
    trailers = Trailer.objects.all()
    return render(request, 'rentalapp/trailer/trailer_list.html', {'trailers': trailers})


@login_required
def trailer_detail(request, pk):
    trailer = get_object_or_404(Trailer, pk=pk)
    service_histories = ServiceHistory.objects.filter(trailer=trailer)

    if trailer.status == 'maintenance':
        active_status = 'maintenance'
    else:
        active_status = 'active' if is_trailer_active(trailer.ip_address) else 'inactive'

    return render(
        request,
        'rentalapp/trailer/trailer_detail.html',
        {
            'trailer': trailer,
            'service_histories': service_histories,
            'active_status': active_status,
        },
    )


@login_required
def trailer_create(request):
    if request.method == 'POST':
        form = TrailerForm(request.POST)
        if form.is_valid():
            trailer = form.save()
            TrailerLog.objects.create(
                trailer=trailer,
                event_type='added',
                message=f"Przyczepka dodana przez {request.user.username}."
            )
            messages.success(request, f"Przyczepka '{trailer.name}' została dodana.")
            return redirect('rentalapp:trailer_detail', pk=trailer.pk)
    else:
        form = TrailerForm()
    return render(request, 'rentalapp/trailer/trailer_create.html', {'form': form})


@login_required
def trailer_edit(request, pk):
    trailer = get_object_or_404(Trailer, pk=pk)
    old_status = trailer.status
    if request.method == 'POST':
        form = TrailerForm(request.POST, instance=trailer)
        if form.is_valid():
            trailer = form.save()
            TrailerLog.objects.create(
                trailer=trailer,
                event_type='edited',
                message=f"Przyczepka edytowana przez {request.user.username}."
            )
            new_status = trailer.status
            if old_status != new_status:
                from django.utils import timezone
                current_time = timezone.now().strftime('%H:%M')
                if new_status == 'maintenance':
                    message_text = f"Status zmieniony na 'W serwisie' przez {request.user.username} o {current_time}"
                else:
                    message_text = f"Status zmieniony na '{trailer.get_status_display()}' o {current_time}"
                TrailerLog.objects.create(
                    trailer=trailer,
                    event_type='status_change',
                    message=message_text
                )
            messages.info(request, f"Przyczepka '{trailer.name}' została zaktualizowana.")
            return redirect('rentalapp:trailer_detail', pk=trailer.pk)
        else:
            print(form.errors)
    else:
        form = TrailerForm(instance=trailer)
    return render(request, 'rentalapp/trailer/trailer_edit.html', {'form': form, 'trailer': trailer})


@login_required
def trailer_delete(request, pk):
    trailer = get_object_or_404(Trailer, pk=pk)

    if request.method == 'POST':
        trailer_name = trailer.name

        TrailerLog.objects.create(
            event_type='deleted',
            message=f"Przyczepka '{trailer_name}' została usunięta przez {request.user.username}"
        )

        trailer.delete()
        messages.success(request, f"Przyczepka '{trailer_name}' została usunięta.")
        return redirect('rentalapp:trailer_list')

    return redirect('rentalapp:trailer_detail', pk=pk)


@login_required
def servicehistory_list(request):
    service_histories = ServiceHistory.objects.select_related('trailer').all()
    return render(request, 'rentalapp/service/servicehistory_list.html', {'service_histories': service_histories})


@login_required
def mark_service_done(request, trailer_id):
    trailer = get_object_or_404(Trailer, id=trailer_id)

    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()

        trailer.status = 'inactive'
        trailer.save()

        TrailerLog.objects.create(
            trailer=trailer,
            event_type='status_change',
            message=f"Przyczepka {trailer.name} zakończyła serwis i została ustawiona jako nieaktywna. Notatka: {comment}"
        )

        ServiceHistory.objects.create(
            trailer=trailer,
            service_date=timezone.now().date(),
            description=f"Zakończono serwis - {comment}",
            cost=0
        )

        messages.success(request, f"Przyczepka {trailer.name} zakończyła serwis.")
        return redirect('rentalapp:active_services_view')

    return render(request, 'rentalapp/service/../templates/rentalapp/mark_service_done.html', {
        'trailer': trailer
    })


# Widok logów
@login_required
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


# Widoki logowania/wylogowania
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Zostałeś zalogowany.")
            return redirect('rentalapp:dashboard')
        else:
            messages.error(request, "Nieprawidłowa nazwa użytkownika lub hasło.")
    return render(request, 'rentalapp/login/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Zostałeś wylogowany.")
    return redirect('rentalapp:login')


@staff_member_required
def assign_role(request):
    if request.method == 'POST':
        form = UserRoleForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"Użytkownik {user.username} otrzymał rolę {role.name}.")
            return redirect('rentalapp:assign_role')
    else:
        form = UserRoleForm()
    return render(request, 'rentalapp/login/assign_role.html', {'form': form})


@login_required
def map_view(request):
    trailers = Trailer.objects.exclude(latitude=None).exclude(longitude=None).values('name', 'latitude', 'longitude')
    total_trailers = Trailer.objects.count()

    context = {
        'trailers_json': list(trailers),
        'total_trailers': total_trailers
    }
    return render(request, 'rentalapp/map_leaflet.html', context)


@login_required
def trailer_logs(request, pk):
    trailer = get_object_or_404(Trailer, pk=pk)
    trailer_logs = trailer.logs.all().order_by('-timestamp')
    return render(request, 'rentalapp/trailer/trailer_logs_partial.html', {
        'trailer': trailer,
        'trailer_logs': trailer_logs
    })


## MAGAZYN


@login_required
def warehouse_manager_view(request):
    items = WarehouseItem.objects.all()
    return render(request, 'rentalapp/warehouse/warehouse_manager.html', {'items': items})


@login_required
def warehouse_add_item_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        date_state = request.POST.get('date_state')
        comment = request.POST.get('comment', '')

        if name and quantity and date_state:
            new_item = WarehouseItem.objects.create(
                name=name,
                quantity=int(quantity),
                date_state=date_state,
                comment=comment
            )
            messages.success(request, f"Dodano przedmiot: {name}")

            from django.utils import timezone
            WarehouseLog.objects.create(
                item=new_item,
                user=request.user,
                quantity_taken=int(quantity),
                message=f"{request.user.username} dodał {quantity} szt. przedmiotu '{new_item.name}'."
            )

            return redirect('rentalapp:warehouse_manager')
        else:
            messages.error(request, "Wypełnij wszystkie wymagane pola.")

    return render(request, 'rentalapp/warehouse/warehouse_add_item.html')


@login_required
def warehouse_delete_item_view(request, pk):
    item = get_object_or_404(WarehouseItem, pk=pk)
    item.delete()
    messages.warning(request, f"Usunięto przedmiot: {item.name}")
    return redirect('rentalapp:warehouse_manager')


@login_required
def warehouse_delete_selected_view(request):
    if request.method == 'POST':
        items_ids = request.POST.getlist('selected_items')
        WarehouseItem.objects.filter(pk__in=items_ids).delete()
        messages.warning(request, f"Usunięto zaznaczone przedmioty.")
    return redirect('rentalapp:warehouse_manager')


@login_required
def warehouse_undo_view(request):
    messages.info(request, "Cofnięto ostatnią operację (funkcjonalność do zaimplementowania).")
    return redirect('rentalapp:warehouse_manager')


@login_required
def warehouse_edit_item_view(request, pk):
    item = get_object_or_404(WarehouseItem, pk=pk)
    old_quantity = item.quantity
    if request.method == "POST":
        form = WarehouseItemForm(request.POST, instance=item)
        if form.is_valid():
            updated_item = form.save()
            new_quantity = updated_item.quantity

            if new_quantity != old_quantity:
                quantity_diff = new_quantity - old_quantity
                abs_diff = abs(quantity_diff)

                if quantity_diff > 0:
                    message_text = f"{request.user.username} dodał {abs_diff} szt. do przedmiotu '{updated_item.name}'."
                else:
                    message_text = f"{request.user.username} zabrał {abs_diff} szt. z przedmiotu '{updated_item.name}'."

                WarehouseLog.objects.create(
                    item=updated_item,
                    user=request.user,
                    quantity_taken=quantity_diff,
                    message=message_text
                )

            messages.success(request, f"Ilość przedmiotu '{updated_item.name}' została zaktualizowana.")
            return redirect('rentalapp:warehouse_manager')
        else:
            messages.error(request, "Formularz zawiera błędy.")
    else:
        form = WarehouseItemForm(instance=item)

    return render(request, "rentalapp/warehouse/warehouse_edit_item.html", {"form": form, "item": item})


@login_required
def warehouse_logs_view(request):
    logs = WarehouseLog.objects.all().order_by('-timestamp')
    return render(request, 'rentalapp/warehouse/warehouse_logs.html', {'logs': logs})


# DASHBOARD
@login_required
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


# wynajmy


@login_required
def company_rent_detail(request, company_id):
    company = get_object_or_404(Company, id=company_id)
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
            return redirect('rentalapp:company_rent_detail', company_id=company.id)

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

            return redirect('rentalapp:company_rent_detail', company_id=company.id)

        elif 'delete_rental' in request.POST:
            RentalHistory.objects.create(
                rental=rental,
                description=f"Wynajem został usunięty.",
                user=request.user
            )
            rental.delete()
            messages.success(request, "Wynajem został usunięty.")
            return redirect('rentalapp:company_rent_detail', company_id=company.id)

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


@login_required
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


@login_required
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


@login_required
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company.delete()
    messages.success(request, "Firma została usunięta.")
    return redirect('rentalapp:rent')


@login_required
def delete_rental(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    rental.delete()
    messages.success(request, "Wynajem został usunięty.")
    return redirect('rentalapp:rent')


@login_required
def company_list_view(request):
    companies = Company.objects.all()

    for company in companies:
        rentals = Rental.objects.filter(company=company)
        company.total_rentals = rentals.count()
        company.total_income = sum(r.cost for r in rentals)

    return render(request, 'rentalapp/rent/company_list.html', {
        'companies': companies
    })


@login_required
def rent_view(request):
    companies = Company.objects.filter(rentals__isnull=False).distinct().prefetch_related('rentals')

    for company in companies:
        company.total_cost = company.rentals.aggregate(total=Sum('cost'))['total'] or 0

    return render(request, 'rentalapp/rent/rent.html', {
        'companies': companies
    })


# serwisy

@login_required
def send_for_service(request, trailer_id):
    trailer = get_object_or_404(Trailer, id=trailer_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        service_type = request.POST.get('service_type')
        location = request.POST.get('location')
        note = request.POST.get('note')

        trailer.status = status
        trailer.notes = note
        trailer.save()

        TrailerLog.objects.create(
            trailer=trailer,
            event_type='status_change',
            message=f"Przyczepka wysłana na serwis ({service_type}) - {note}"
        )

        ServiceHistory.objects.create(
            trailer=trailer,
            service_date=timezone.now().date(),
            description=f"{service_type} - {note}",
            cost=0
        )

        if service_type.lower() == 'transport':
            RentalTrailer.objects.filter(trailer=trailer).delete()
            messages.info(request, f"Przyczepka {trailer.name} została usunięta z wynajmów i wysłana na transport.")
        else:
            messages.success(request, f"Przyczepka {trailer.name} została wysłana na serwis.")

        return redirect('rentalapp:trailer_detail', trailer_id)

    return render(request, 'rentalapp/service/send_for_service.html', {
        'trailer': trailer
    })


@login_required
def service_history_view(request):
    services = ServiceHistory.objects.select_related('trailer').order_by('-service_date')
    return render(request, 'rentalapp/service/servicehistory_list.html', {'service_histories': services})


@login_required
def active_services_view(request):
    trailers_in_service = Trailer.objects.filter(status='maintenance')
    return render(request, 'rentalapp/service/active_services.html', {
        'trailers': trailers_in_service
    })


@login_required
def mark_service_done(request, trailer_id):
    trailer = get_object_or_404(Trailer, id=trailer_id)

    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()

        ServiceHistory.objects.create(
            trailer=trailer,
            service_date=timezone.now().date(),
            description=comment or "Serwis zakończony bez opisu.",
            cost=0
        )

        trailer.status = 'inactive'
        trailer.save()

        TrailerLog.objects.create(
            trailer=trailer,
            event_type='status_change',
            message=f"Przyczepka {trailer.name} zakończyła serwis. Notatka: {comment}"
        )

        messages.success(request, f"Przyczepka {trailer.name} zakończyła serwis.")
        return redirect('rentalapp:service_history_view')

    return render(request, 'rentalapp/service/mark_service_done.html', {
        'trailer': trailer
    })


@login_required
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


@login_required
def rental_history_view(request):
    rentals = Rental.objects.select_related('company').prefetch_related('rental_trailers__trailer')
    return render(request, 'rentalapp/rent/rental_history.html', {
        'rentals': rentals
    })
