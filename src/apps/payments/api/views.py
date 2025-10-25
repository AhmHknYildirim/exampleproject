# src/apps/payments/api/views_viewset.py
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from src.apps.core.models import Payments
from .serializers import (
    PaymentSerializer,
    PaymentInitiateSerializer,
    PaymentTransitionSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = (
        Payments.objects
        .select_related("status", "repair", "repair__vehicle", "repair__customer")
        .all()
        .order_by("-payment_date", "-id")
    )
    serializer_class = PaymentSerializer

    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    search_fields = (
        "transaction_id",
        "gateway_ref",
        "repair__vehicle__vin",
        "repair__customer__first_name",
        "repair__customer__last_name",
    )
    ordering_fields = ("payment_date", "amount", "currency")
    filterset_fields = {
        "status": ["exact"],
        "currency": ["exact"],
        "repair": ["exact"],
        "payment_date": ["gte", "lte"],
    }

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentInitiateSerializer
        return PaymentSerializer

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        payment = self.get_object()
        ser = PaymentTransitionSerializer(instance=payment, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
