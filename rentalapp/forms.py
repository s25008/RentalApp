from django import forms
from .models import Trailer, Company, Rental, WarehouseItem
from django.contrib.auth.models import User, Group


class TrailerForm(forms.ModelForm):
    class Meta:
        model = Trailer
        fields = [
            'name',
            'ip_address',
            'serial_number',
            'registration_number',
            'operator_phone',
            'location_link',
            'notes',
            'status',
        ]


class UserRoleForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Użytkownik")
    role = forms.ModelChoiceField(queryset=Group.objects.all(), label="Rola")


class WarehouseItemForm(forms.ModelForm):
    class Meta:
        model = WarehouseItem
        fields = ['quantity']


class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['name','company', 'start_date', 'end_date', 'monthly_price']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'monthly_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'phone', 'email']
        labels = {
            'name': 'Nazwa firmy',
            'phone': 'Telefon',
            'email': 'Email',
        }

