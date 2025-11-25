import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

# Primero inicializamos Django (esto carga apps y modelos)
django_asgi_app = get_asgi_application()

# IMPORTAMOS routing DESPUÉS de que Django ya está inicializado
import screens.routing  # noqa: E402


application = ProtocolTypeRouter(
    {
        # Ahora HTTP pasa por el handler que sirve /static/*
        "http": ASGIStaticFilesHandler(django_asgi_app),
        "websocket": AuthMiddlewareStack(
            URLRouter(screens.routing.websocket_urlpatterns)
        ),
    }
)
