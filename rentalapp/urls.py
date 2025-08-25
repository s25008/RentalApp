from django.urls import path
from . import views

app_name = 'rentalapp'

urlpatterns = [
    # Strona główna oraz logowanie/wylogowanie
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Pozostałe widoki
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('map/', views.map_view, name='map_view'),
    path('history/', views.history_view, name='history'),
    path('assign-role/', views.assign_role, name='assign_role'),
    path('rental-history/', views.rental_history_view, name='rental_history'),

    # wynajmy
    path('rent/', views.rent_view, name='rent'),
    path('rent/company/<int:pk>/', views.company_rent_detail, name='company_rent_detail'),
    path('trailer/<int:pk>/', views.trailer_detail, name='trailer_detail'),
    path('rent/add/', views.add_rental, name='add_rental'),
    path('company/add/', views.add_company, name='add_company'),
    path('company/delete/<int:pk>/', views.delete_company, name='delete_company'),
    path('rental/delete/<int:pk>/', views.delete_rental, name='delete_rental'),
    path('companies/', views.company_list_view, name='company_list'),

    # Serwisy
    path('trailer/<int:pk>/service/', views.send_for_service, name='send_for_service'),
    path('service/active/', views.active_services_view, name='active_services_view'),
    path('service/done/<int:pk>/', views.mark_service_done, name='mark_service_done'),
    path('service-history/', views.service_history_view, name='service_history_view'),

    # Widoki dotyczące przyczepek
    path('trailers/', views.trailer_list, name='trailer_list'),
    path('trailers/create/', views.trailer_create, name='trailer_create'),
    path('trailers/<int:pk>/', views.trailer_detail, name='trailer_detail'),
    path('trailers/<int:pk>/edit/', views.trailer_edit, name='trailer_edit'),
    path('servicehistory/', views.servicehistory_list, name='servicehistory_list'),
    path('trailer/<int:pk>/logs/', views.trailer_logs, name='trailer_logs'),
    path('trailers/<int:pk>/delete/', views.trailer_delete, name='trailer_delete'),

    # Widok logów
    path('log/', views.logs_view, name='log'),

    # Widoki zarządzania magazynem
    path('warehouse/', views.warehouse_manager_view, name='warehouse_manager'),
    path('warehouse/add/', views.warehouse_add_item_view, name='warehouse_add_item'),
    path('warehouse/delete/<int:pk>/', views.warehouse_delete_item_view, name='warehouse_delete_item'),
    path('warehouse/delete_selected/', views.warehouse_delete_selected_view, name='warehouse_delete_selected'),
    path('warehouse/undo/', views.warehouse_undo_view, name='warehouse_undo'),
    path('warehouse/<int:pk>/edit/', views.warehouse_edit_item_view, name='warehouse_edit_item'),
    path('warehouse/logs/', views.warehouse_logs_view, name='warehouse_logs'),

    # pdf
    path('report/pdf/', views.generate_report_pdf, name='generate_report_pdf'),
]
