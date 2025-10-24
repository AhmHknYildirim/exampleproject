from django.db import models

from src.apps.core.managers import ActiveManager


class PaymentsStatus(models.Model):
    payment_status_text = models.CharField(max_length=64, default="Initiated")
    payment_status_align = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    all_objects = models.Manager()
    objects = ActiveManager()

class RentalsStatus(models.Model):
    rental_status_text = models.CharField(max_length=64, default="Initiated")
    rental_status_align = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    all_objects = models.Manager()
    objects = ActiveManager()

class RepairsStatus(models.Model):
    repair_status_text = models.CharField(max_length=64, default="Initiated")
    repair_status_align = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    all_objects = models.Manager()
    objects = ActiveManager()

class Vehicles(models.Model):
    text = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    vin = models.CharField(max_length=17, unique=True)
    is_active = models.BooleanField(default=True)
    all_objects = models.Manager()
    objects = ActiveManager()

    def __str__(self):
        return f"{self.year} {self.text} {self.model} ({self.vin})"

class Customers(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    identity_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    all_objects = models.Manager()
    objects = ActiveManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Payments(models.Model):
    repair = models.OneToOneField("RepairOrders", on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default="GBP")
    status = models.ForeignKey(PaymentsStatus, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    gateway_ref = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    all_objects = models.Manager()
    objects = ActiveManager()

    def __str__(self):
        return f"Payment {self.amount} {self.currency} for {self.repair_id}"

class RepairOrders(models.Model):
    vehicle = models.ForeignKey("Vehicles", on_delete=models.CASCADE)
    customer = models.ForeignKey("Customers", on_delete=models.CASCADE)
    status = models.ForeignKey(RepairsStatus, on_delete=models.CASCADE, related_name="repair_orders")
    description = models.TextField()
    repair_date = models.DateTimeField(auto_now_add=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    all_objects = models.Manager()
    objects = ActiveManager()

    def __str__(self):
        return f"Repair Order for {self.vehicle} on {self.repair_date}"

class Rentals(models.Model):
    vehicle = models.ForeignKey("Vehicles", on_delete=models.CASCADE)
    customer = models.ForeignKey("Customers", on_delete=models.CASCADE)
    repair = models.ForeignKey("RepairOrders", on_delete=models.SET_NULL, blank=True, null=True)
    status = models.ForeignKey(RentalsStatus, on_delete=models.CASCADE, related_name="rentals")
    rental_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(blank=True, null=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    all_objects = models.Manager()
    objects = ActiveManager()

    def __str__(self):
        return f"Rental for {self.vehicle} on {self.customer}"