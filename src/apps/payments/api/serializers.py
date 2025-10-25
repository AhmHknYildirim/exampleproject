from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoVE
from rest_framework import serializers

from src.apps.core.models import (
    Payments, PaymentsStatus, RepairOrders, RepairsStatus
)
from src.apps.core.validator import validate_payment_transition, validate_payment_initiate

MONEY_Q = Decimal("0.01")


class PaymentSerializer(serializers.ModelSerializer):
    repair_vehicle_vin = serializers.CharField(source="repair.vehicle.vin", read_only=True)
    repair_customer = serializers.SerializerMethodField(read_only=True)
    status_text = serializers.CharField(source="status.payment_status_text", read_only=True)
    status_align = serializers.IntegerField(source="status.payment_status_align", read_only=True)

    class Meta:
        model = Payments
        fields = (
            "id",
            "repair",
            "amount",
            "currency",
            "status",
            "status_text",
            "status_align",
            "payment_date",
            "transaction_id",
            "gateway_ref",
            "repair_vehicle_vin",
            "repair_customer",
        )
        read_only_fields = ["id", "payment_date", "status"]

    def get_repair_customer(self, obj):
        c = obj.repair.customer
        return f"{c.first_name} {c.last_name}".strip()

    def validate_amount(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError("Amount must be ≥ 0.")
        return value.quantize(MONEY_Q, rounding=ROUND_HALF_UP)

    def validate_currency(self, value):
        if not value:
            return "GBP"
        v = value.upper()
        if len(v) > 8:
            raise serializers.ValidationError("Currency must be ≤ 8 chars.")
        return v

class PaymentInitiateSerializer(PaymentSerializer):
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentsStatus.objects.all(),
        source="status",
        write_only=True,
        required=False,
    )

    class Meta(PaymentSerializer.Meta):
        fields = (
            "id",
            "repair",
            "amount",
            "currency",
            "status",
            "status_id",
            "payment_date",
            "transaction_id",
            "gateway_ref",
            "status_text",
            "status_align",
            "repair_vehicle_vin",
            "repair_customer",
        )
        read_only_fields = ["id", "payment_date", "status"]

    def validate(self, attrs):
        repair: RepairOrders = attrs["repair"]
        try:
            validate_payment_initiate(repair)
        except DjangoVE as e:
            raise serializers.ValidationError({"repair": e.message})

        ps = attrs.get("status")
        if ps and ps.payment_status_text.lower() != "initiated":
            raise serializers.ValidationError({"status_id": "Status must be 'Initiated' at creation."})
        if not ps:
            ps = PaymentsStatus.objects.get(payment_status_text__iexact="initiated")
            attrs["status"] = ps

        attrs["amount"] = self.validate_amount(attrs["amount"])
        attrs["currency"] = self.validate_currency(attrs.get("currency") or "GBP")

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        repair = (
            RepairOrders.objects
            .select_for_update()
            .select_related("status")
            .get(pk=validated_data["repair"].pk)
        )
        tx = validated_data.get("transaction_id")
        if tx:
            existing = Payments.objects.filter(transaction_id=tx).first()
            if existing:
                return existing

        return super().create(validated_data)


class PaymentTransitionSerializer(serializers.ModelSerializer):
    target_status_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentsStatus.objects.all(),
        write_only=True
    )

    class Meta:
        model = Payments
        fields = ["target_status_id", "status"]
        read_only_fields = ["status"]

    def validate(self, attrs):
        payment: Payments = self.instance
        target = attrs["target_status_id"]
        try:
            validate_payment_transition(payment, target)
        except DjangoVE as e:
            raise serializers.ValidationError({"target_status_id": e.message})
        attrs["_target"] = target
        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        target: PaymentsStatus = validated_data["_target"]
        instance.status = target
        instance.save(update_fields=["status"])

        if target.payment_status_text.lower() == "verified":
            paid = RepairsStatus.objects.get(repair_status_text__iexact="paid")
            repair = (
                RepairOrders.objects
                .select_for_update()
                .get(pk=instance.repair_id)
            )
            repair.status = paid
            repair.save(update_fields=["status"])
        return instance