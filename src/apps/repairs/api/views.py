from django.db.models import Q
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils.dateparse import parse_date, parse_datetime

from src.apps.core.models import RepairOrders
from src.apps.repairs.api.serializers import RepairOrdersSerializer


class RepairsOrderViewSet(viewsets.ModelViewSet):
    queryset = (
        RepairOrders.objects
        .select_related("vehicle", "customer", "status")
        .all()
    )
    serializer_class = RepairOrdersSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    search_fields = (
        "description",
        "vehicle__vin",
        "vehicle__text",
        "vehicle__model",
        "customer__first_name",
        "customer__last_name",
        "customer__email",
    )

    ordering_fields = (
        "repair_date",
        "completed_at",
        "estimated_cost",
        "vehicle__text",
        "customer__last_name",
    )
    ordering = ("-repair_date",)

    def get_queryset(self):
        qs = super().get_queryset()

        status_id   = self.request.query_params.get("status_id")
        vehicle_id  = self.request.query_params.get("vehicle_id")
        customer_id = self.request.query_params.get("customer_id")

        date_from = self.request.query_params.get("date_from")
        date_to   = self.request.query_params.get("date_to")

        if status_id:
            qs = qs.filter(status_id=status_id)
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)

        if date_from:
            d = parse_date(date_from) or parse_datetime(date_from)
            if not d:
                raise ValidationError({"date_from": "Enter a valid date/time."})
            if hasattr(d, "year") and not hasattr(d, "hour"):
                qs = qs.filter(repair_date__date__gte=d)
            else:
                qs = qs.filter(repair_date__gte=d)

        if date_to:
            d = parse_date(date_to) or parse_datetime(date_to)
            if not d:
                raise ValidationError({"date_to": "Enter a valid date/time."})
            if hasattr(d, "year") and not hasattr(d, "hour"):
                qs = qs.filter(repair_date__date__lte=d)
            else:
                qs = qs.filter(repair_date__lte=d)

        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(instance, "is_active"):
            instance.is_active = False
            instance.save(update_fields=["is_active"])
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)
