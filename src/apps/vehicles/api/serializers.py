from rest_framework import serializers
from src.apps.core.models import (
    Vehicles
)

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicles
        fields = ["id", "text", "model", "year", "vin"]
        read_only_fields = ["id"]

    def validate_year(self, value: int):
        if value < 1886 or value > 2100:
            raise serializers.ValidationError("Year must be between 1886 and 2100.")
        return value

    def validate_vin(self, value: str):
        if len(value) != 17:
            raise serializers.ValidationError("VIN must be 17 characters.")
        forbidden = {"O", "I", "Q"}
        if any(ch in forbidden for ch in value.upper()):
            raise serializers.ValidationError("VIN must not contain I, O, or Q.")
        return value.upper()