from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RepairsOrderViewSet

app_name = "repairs"

router = DefaultRouter()
router.register(r"repair-orders", RepairsOrderViewSet, basename="repair-orders")

urlpatterns = [
    path("", include(router.urls)),
]
