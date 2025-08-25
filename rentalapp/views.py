from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .modules.auth import AuthViews
from .modules.dashboard import DashboardViews
from .modules.logs import LogsViews
from .modules.map import MapViews
from .modules.rent import RentViews
from .modules.reports import ReportsViews
from .modules.service import ServiceViews
from .modules.trailer import TrailerViews
from .modules.warehouse import WarehouseViews


@login_required
def history_view(request):
    return render(request, 'rentalapp/history.html')


#PRZYCZEPKI

@login_required
def trailer_list(request):
    return TrailerViews.trailer_list(request)

@login_required
def trailer_detail(request, pk):
    return TrailerViews.trailer_detail(request, pk)

@login_required
def trailer_create(request):
    return TrailerViews.trailer_create(request)

@login_required
def trailer_edit(request, pk):
    return TrailerViews.trailer_edit(request, pk)

@login_required
@require_POST
def trailer_delete(request, pk):
    return TrailerViews.trailer_delete(request, pk)

@login_required
def trailer_logs(request, pk):
    return LogsViews.trailer_logs(request, pk)


#LOGI

@login_required
def logs_view(request):
    return LogsViews.logs_view(request)


#AUTH

def login_view(request):
    return AuthViews.login_view(request)

def logout_view(request):
    return AuthViews.logout_view(request)

@staff_member_required
def assign_role(request):
    return AuthViews.assign_role(request)


#MAPA

@login_required
def map_view(request):
    return MapViews.map_view(request)


#MAGAZYN

@login_required
def warehouse_manager_view(request):
    return WarehouseViews.warehouse_manager_view(request)

@login_required
def warehouse_add_item_view(request):
    return WarehouseViews.warehouse_add_item_view(request)

@login_required
@require_POST
def warehouse_delete_item_view(request, pk):
    return WarehouseViews.warehouse_delete_item_view(request, pk)

@login_required
@require_POST
def warehouse_delete_selected_view(request):
    return WarehouseViews.warehouse_delete_selected_view(request)

@login_required
def warehouse_undo_view(request):
    return WarehouseViews.warehouse_undo_view(request)

@login_required
def warehouse_edit_item_view(request, pk):
    return WarehouseViews.warehouse_edit_item_view(request, pk)

@login_required
def warehouse_logs_view(request):
    return LogsViews.warehouse_logs_view(request)


#DASHBOARD

@login_required
def dashboard_view(request):
    return DashboardViews.dashboard_view(request)


#WYNAJMY/FIRMY

@login_required
def company_rent_detail(request, pk):
    return RentViews.company_rent_detail(request, pk)

@login_required
def add_rental(request):
    return RentViews.add_rental(request)

@login_required
def add_company(request):
    return RentViews.add_company(request)

@login_required
@require_POST
def delete_company(request, pk):
    return RentViews.delete_company(request, pk)

@login_required
@require_POST
def delete_rental(request, pk):
    return RentViews.delete_rental(request, pk)

@login_required
def company_list_view(request):
    return RentViews.company_list_view(request)

@login_required
def rent_view(request):
    return RentViews.rent_view(request)

@login_required
def rental_history_view(request):
    return RentViews.rental_history_view(request)


#SERWISY

@login_required
def servicehistory_list(request):
    return ServiceViews.servicehistory_list(request)

@login_required
def service_history_view(request):
    return ServiceViews.service_history_view(request)

@login_required
def active_services_view(request):
    return ServiceViews.active_services_view(request)

@login_required
def send_for_service(request, pk):
    return ServiceViews.send_for_service(request, pk)

@login_required
def mark_service_done(request, pk):
    return ServiceViews.mark_service_done(request, pk)


#RAPORT PDF

@login_required
def generate_report_pdf(request):
    return ReportsViews.generate_report_pdf(request)
