from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipmentItemViewSet

router = DefaultRouter()
router.register(r"", EquipmentItemViewSet, basename="equipment")

urlpatterns = [
    path("", include(router.urls)),
]
