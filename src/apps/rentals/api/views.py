from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from src.apps.core.models import Rentals
from .serializers import (
    RentalSerializer,
    RentalStatusUpdateSerializer,
    RentalReturnSerializer,
)

class RentalViewSet(viewsets.ModelViewSet):
    queryset = (
        Rentals.objects
        .select_related("vehicle", "customer", "status", "repair")
        .all()
    )
    serializer_class = RentalSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    search_fields = (
        "vehicle__vin", "vehicle__text", "vehicle__model",
        "customer__first_name", "customer__last_name", "customer__email",
    )
    ordering_fields = ("rental_date", "return_date", "price_per_day")
    ordering = ("-rental_date",)
    filterset_fields = {
        "status": ["exact"],
        "customer": ["exact"],
        "vehicle": ["exact"],
        "rental_date": ["gte", "lte"],
        "return_date": ["isnull"],
    }

    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        rental = self.get_object()
        ser = RentalStatusUpdateSerializer(instance=rental, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(RentalSerializer(rental).data)

    @action(detail=True, methods=["post"], url_path="return")
    def return_car(self, request, pk=None):
        rental = self.get_object()
        ser = RentalReturnSerializer(instance=rental, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(RentalSerializer(rental).data, status=status.HTTP_200_OK)
