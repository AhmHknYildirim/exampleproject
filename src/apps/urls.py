from django.urls import path, include

urlpatterns = [
    path("", include(("src.apps.vehicles.api.urls", "vehicles"), namespace="vehicles")),
    path("", include(("src.apps.customers.api.urls", "customers"), namespace="customers")),
    path("", include(("src.apps.repairs.api.urls", "repairs"), namespace="repairs")),
    path("", include(("src.apps.rentals.api.urls", "rentals"), namespace="rentals")),
    path("", include(("src.apps.payments.api.urls", "payments"), namespace="payments")),
]
