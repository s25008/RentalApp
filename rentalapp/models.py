from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Trailer(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    serial_number = models.CharField(max_length=100, unique=True)
    registration_number = models.CharField(max_length=20)
    operator_phone = models.CharField(max_length=20)
    location_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    STATUS_CHOICES = [
        ('active', 'Aktywna'),
        ('inactive', 'Nieaktywna'),
        ('maintenance', 'W serwisie')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name


class Rental(models.Model):
    name = models.CharField(max_length=255, default="", blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='rentals')
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        days = (self.end_date - self.start_date).days + 1
        daily_rate = self.monthly_price / 30
        self.cost = round(days * daily_rate, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Wynajem #{self.id} - {self.company.name}"


class RentalTrailer(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='rental_trailers')
    trailer = models.ForeignKey(Trailer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.trailer.name} (Rental #{self.rental.id})"


class ServiceHistory(models.Model):
    trailer = models.ForeignKey(Trailer, on_delete=models.CASCADE, related_name='service_histories')
    service_date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Serwis {self.trailer.name} dnia {self.service_date}"


class TrailerLog(models.Model):
    EVENT_TYPE_CHOICES = [
        ('added', 'Dodano przyczepkę'),
        ('edited', 'Edytowano przyczepkę'),
        ('deleted', 'Usunięto przyczepkę'),
        ('status_change', 'Zmiana statusu'),
        ('ping', 'Pingowanie'),
    ]

    timestamp = models.DateTimeField(default=now)
    trailer = models.ForeignKey('Trailer', on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    message = models.TextField()

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.trailer.name if self.trailer else 'Usunięta przyczepka'} ({self.timestamp})"


class WarehouseItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    date_state = models.DateField()
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class WarehouseLog(models.Model):
    timestamp = models.DateTimeField(default=now)
    item = models.ForeignKey(WarehouseItem, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_taken = models.IntegerField(default=0)
    message = models.TextField()

    def __str__(self):
        return f"{self.user.username if self.user else 'System'}: {self.message}"


class RentalHistory(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='history')
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.rental} - {self.description}"
