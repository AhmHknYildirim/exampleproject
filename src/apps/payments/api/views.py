from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from celery.result import AsyncResult

from src.apps.core.models import Payments
from .serializers import (
    PaymentSerializer,
    PaymentInitiateSerializer,
    PaymentTransitionSerializer,
)
from src.apps.payments.tasks import verify_payment_and_mark_repair_paid

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = (
        Payments.objects
        .select_related("status", "repair", "repair__vehicle", "repair__customer")
        .all()
        .order_by("-payment_date", "-id")
    )
    serializer_class = PaymentSerializer
    permission_classes = [permissions.AllowAny] #or IsAuthenticated

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
        if self.action == "transition":
            return PaymentTransitionSerializer
        return PaymentSerializer

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        payment = self.get_object()
        ser = PaymentTransitionSerializer(instance=payment, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Trigger async verification for this payment’s repair",
        responses={202: OpenApiResponse(description="Task accepted")},
        tags=["payments", "tasks"],
    )
    @action(detail=True, methods=["post"], url_path="verify-async")
    def verify_async(self, request, pk=None):
        payment = self.get_object()
        task = verify_payment_and_mark_repair_paid.delay(payment.repair_id)
        return Response(
            {"message": "Task accepted", "task_id": task.id, "repair_id": payment.repair_id},
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(
        parameters=[OpenApiParameter(name="task_id", required=True, location=OpenApiParameter.PATH, type=str)],
        summary="Get Celery task status/result",
        tags=["tasks"],
    )
    @action(detail=False, methods=["get"], url_path=r"tasks/(?P<task_id>[^/.]+)")
    def task_status(self, request, task_id=None):
        res = AsyncResult(task_id)
        payload = {"task_id": task_id, "status": res.status}
        if res.status == "SUCCESS":
            payload["result"] = res.result
        if res.status == "FAILURE":
            payload["error"] = str(res.result)
        return Response(payload)
