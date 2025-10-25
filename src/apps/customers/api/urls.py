from django.urls import path

from src.apps.customers.api.views import (
    CustomerListCreateAPIView,
    CustomerDetailAPIView
)
app_name = "customers"

urlpatterns = [
    path("customers/", CustomerListCreateAPIView.as_view(), name="customer-list-create"),
    path("customers/<int:pk>/", CustomerDetailAPIView.as_view(), name="customer-detail"),
]
