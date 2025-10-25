from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoVE
from src.apps.core.models import (
    RepairOrders,
    RepairsStatus
)
from src.apps.core.validator import (
    validate_repair_transition,
    apply_completed_timestamp_if_needed
)


class RepairOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrders
        fields = (
            "id",
            "vehicle",
            "customer",
            "status",
            "description",
            "repair_date",
            "estimated_cost",
            "completed_at",
        )

    def validate(self, attrs):
        instance: RepairOrders = self.instance
        new_status: RepairsStatus = attrs["status"]
        try:
            validate_repair_transition(instance, new_status)
        except DjangoVE as e:
            raise serializers.ValidationError({"target_status_id": e.message})
        return attrs

    def update(self, instance, validated_data):
        new_status: RepairsStatus = validated_data["status"]
        apply_completed_timestamp_if_needed(instance, new_status)
        instance.status = new_status
        instance.save(update_fields=["status", "completed_at", "updated_at"])
        return instance