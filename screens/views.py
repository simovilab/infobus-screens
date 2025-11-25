from django.shortcuts import render, get_object_or_404

from .models import Device


def screen_view(request, device_id):
    """
    Vista que sirve el HTML de la pantalla para un dispositivo dado.
    El JS interno se encargará de:
    - llamar a /api/devices/<id>/config/
    - abrir el WebSocket
    - renderizar el layout con Vue
    """
    device = get_object_or_404(Device, id=device_id, is_active=True)
    return render(
        request,
        "screens/screen_view.html",
        {
            "device": device,
        },
    )
