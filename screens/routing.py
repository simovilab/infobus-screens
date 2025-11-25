from django.urls import re_path

from .consumers import DeviceConsumer, PingConsumer

websocket_urlpatterns = [
    # Ruta de prueba súper simple
    re_path(r"^ws/ping/$", PingConsumer.as_asgi()),

    # Ruta de devices (la vamos a simplificar un toque)
    re_path(
        r"^ws/devices/(?P<device_id>[^/]+)/$",
        DeviceConsumer.as_asgi(),
    ),
]
