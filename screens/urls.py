from rest_framework.routers import DefaultRouter

from .api import (
    DeviceGroupViewSet,
    DeviceViewSet,
    DistributionChannelViewSet,
    ScreenTemplateViewSet,
)

router = DefaultRouter()
router.register(r"device-groups", DeviceGroupViewSet)
router.register(r"devices", DeviceViewSet)
router.register(r"channels", DistributionChannelViewSet)
router.register(r"templates", ScreenTemplateViewSet)

urlpatterns = router.urls
