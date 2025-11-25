from django.urls import path
from rest_framework.routers import DefaultRouter

from .api import (
    DeviceGroupViewSet,
    DeviceViewSet,
    DistributionChannelViewSet,
    ScreenTemplateViewSet,
)
from . import views

router = DefaultRouter()
router.register(r"device-groups", DeviceGroupViewSet)
router.register(r"devices", DeviceViewSet)
router.register(r"channels", DistributionChannelViewSet)
router.register(r"templates", ScreenTemplateViewSet)

urlpatterns = [
    # Vista HTML de la pantalla
    path("screens/<uuid:device_id>/", views.screen_view, name="screen_view"),
]

# Rutas de API
urlpatterns += router.urls