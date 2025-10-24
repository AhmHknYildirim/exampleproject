from django.contrib import admin
from .models import (
    Vehicles, Customers, RepairOrders, Payments, Rentals,
    RepairsStatus, PaymentsStatus, RentalsStatus
)
admin.site.register([
    Vehicles, Customers, RepairOrders, Payments, Rentals,
    RepairsStatus, PaymentsStatus, RentalsStatus
])
