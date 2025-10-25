from django.urls import path

from src.apps.vehicles.api.views import (
    VehicleListCreateView,
    VehicleRetrieveUpdateDestroyView
)
app_name = "vehicles"

urlpatterns = [
    path("vehicles/", VehicleListCreateView.as_view(), name="vehicle-list"),
    path("vehicles/<int:pk>/", VehicleRetrieveUpdateDestroyView.as_view(), name="vehicle-detail"),
]