from django.urls import path, include

urlpatterns = [
    path("", include("src.apps.vehicles.api.urls")),
    path("", include("src.apps.customers.api.urls")),
    path("", include("src.apps.repairs.api.urls")),
    path("", include("src.apps.rentals.api.urls")),
    path("", include("src.apps.payments.api.urls")),
]
