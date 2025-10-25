from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from src.apps.core.models import Vehicles
from .serializers import VehicleSerializer

class VehicleListCreateView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericAPIView
):
    queryset = Vehicles.objects.all().order_by("-id")
    serializer_class = VehicleSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class VehicleRetrieveUpdateDestroyView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericAPIView
):
    queryset = Vehicles.objects.all()
    serializer_class = VehicleSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if getattr(instance, "is_active", True):
            instance.is_active = False
            instance.save(update_fields=["is_active"])
