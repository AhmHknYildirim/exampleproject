from rest_framework.routers import DefaultRouter

from src.apps.payments.api.views import PaymentViewSet

app_name = "payments"
router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")
urlpatterns = router.urls
