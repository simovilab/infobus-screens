from django.shortcuts import render, get_object_or_404

from .models import Device


def home(request):
    """
    Página de inicio del servidor de pantallas SIMOVILAB.
    Muestra el logo y un acceso al panel de administración.
    """
    return render(request, "screens/home.html")

def screen_view(request, device_id):
    """
    Vista que sirve el HTML de la pantalla para un dispositivo dado.
    El JS interno se encargará de:
    - llamar a /api/devices/<id>/config/
    - abrir el WebSocket
    - renderizar el layout con Vue
    """
    device = get_object_or_404(Device, id=device_id, is_active=True)

    if device.device_type == Device.DeviceType.ONBOARD:
        template_name = "screens/screen_onboard.html"
    else:
        template_name = "screens/screen_stop.html"

    return render(
        request,
        template_name,
        {
            "device": device,
        },
    )