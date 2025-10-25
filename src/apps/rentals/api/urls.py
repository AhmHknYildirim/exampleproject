from rest_framework.routers import DefaultRouter

from src.apps.rentals.api.views import RentalViewSet

router = DefaultRouter()
router.register(r"rentals", RentalViewSet, basename="rental")
urlpatterns = router.urls
