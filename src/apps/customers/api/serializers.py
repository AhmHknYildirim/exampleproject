from rest_framework import serializers
from src.apps.core.models import Customers

class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customers
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "identity_number"
        )
        read_only_fields = ["id", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def validate_email(self, value: str):
        qs = Customers.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_identity_number(self, value: str):
        if not value:
            return value
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) not in (11, 8, 10):
            raise serializers.ValidationError("Identity number length is not valid.")
        return value

    def validate_phone_number(self, value: str):
        if not value:
            return value
        value = value.replace(" ", "").replace("-", "")
        return value
