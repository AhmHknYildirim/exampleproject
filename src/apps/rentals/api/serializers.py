from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoVE

from src.apps.core.models import Rentals, RentalsStatus
from src.apps.core.validator import validate_rental_transition


class RentalSerializer(serializers.ModelSerializer):
    vehicle_text   = serializers.CharField(source="vehicle.text", read_only=True)
    vehicle_model  = serializers.CharField(source="vehicle.model", read_only=True)
    customer_name  = serializers.SerializerMethodField(read_only=True)
    status_text    = serializers.CharField(source="status.payment_status_text", read_only=True)
    status_align   = serializers.IntegerField(source="status.payment_status_align", read_only=True)

    class Meta:
        model = Rentals
        fields = (
            "id",
            "vehicle",
            "vehicle_text",
            "vehicle_model",
            "customer",
            "customer_name",
            "repair",
            "status",
            "status_text",
            "status_align",
            "rental_date",
            "return_date",
            "price_per_day",
    )
        read_only_fields = ["id", "rental_date"]

    def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}".strip()

    def validate_price_per_day(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError("price_per_day must be ≥ 0.")
        return value

    def validate(self, attrs):
        ret = attrs.get("return_date")
        if ret and self.instance:
            if ret < self.instance.rental_date:
                raise serializers.ValidationError({"return_date": "Return date cannot be earlier than rentals date."})
        return attrs


class RentalStatusUpdateSerializer(serializers.ModelSerializer):
    target_status_id = serializers.PrimaryKeyRelatedField(
        queryset=RentalsStatus.objects.all(),
        write_only=True
    )

    class Meta:
        model = Rentals
        fields = ["target_status_id", "status"]
        read_only_fields = ["status"]

    def validate(self, attrs):
        rental: Rentals = self.instance
        target: RentalsStatus = attrs["target_status_id"]
        try:
            validate_rental_transition(rental, target)
        except DjangoVE as e:
            raise serializers.ValidationError({"target_status_id": e.message})
        return attrs

    def update(self, instance, validated_data):
        target: RentalsStatus = validated_data["target_status_id"]
        instance.status = target
        instance.save(update_fields=["status", "updated_at"])
        return instance


class RentalReturnSerializer(serializers.ModelSerializer):
    return_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Rentals
        fields = ["return_date"]

    def update(self, instance, validated_data):
        instance.return_date = validated_data.get("return_date") or timezone.now()
        instance.save(update_fields=["return_date", "updated_at"])
        return instance
