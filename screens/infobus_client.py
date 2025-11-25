from datetime import datetime, timedelta
import random


def _now_iso():
    return datetime.utcnow().isoformat() + "Z"


def _fake_occupancy():
    return random.choice(["low", "medium", "high"])


def get_onboard_context_for_device(device):
    """
    Devuelve un contexto tipo 'onboard':
    - próxima parada
    - siguientes paradas
    - ETA
    - ocupación
    - alertas
    """
    # Podemos usar group.code como código de ruta si está definido
    route_code = None
    route_name = None
    if device.group:
        route_code = device.group.code or f"R-{device.group.id}"
        route_name = device.group.name
    else:
        route_code = "R-101"
        route_name = "Ruta demo - Centro"

    # Podemos usar metadata para info del bus si existe
    bus_id = device.metadata.get("bus_id", f"BUS-{str(device.id)[:8]}")
    plate = device.metadata.get("plate", "XXX-123")

    # Paradas de ejemplo
    stops = [
        {"code": "STOP-TEC", "name": "TEC Cartago"},
        {"code": "STOP-PLAZA", "name": "Plaza Mayor"},
        {"code": "STOP-CENTRO", "name": "Centro Cartago"},
        {"code": "STOP-TERMINAL", "name": "Terminal Norte"},
    ]
    current_stop = random.choice(stops[:-1])
    next_stop = random.choice(stops[1:])
    following_stops = [s for s in stops if s != current_stop and s != next_stop][:3]

    eta_minutes = random.randint(2, 10)

    context = {
        "context_type": "onboard",
        "timestamp": _now_iso(),
        "route": {
            "code": route_code,
            "name": route_name,
        },
        "bus": {
            "id": bus_id,
            "plate": plate,
        },
        "current_stop": current_stop,
        "next_stop": next_stop,
        "following_stops": following_stops,
        "eta_next_stop_minutes": eta_minutes,
        "eta_next_stop_human": f"{eta_minutes} min",
        "connections": [
            {
                "route_code": "R-201",
                "route_name": "Ruta demo conexión",
                "eta_minutes": random.randint(5, 20),
            }
        ],
        "alerts": [
            {
                "level": "info",
                "code": "DEMO",
                "message": "Servicio de demostración.",
            }
        ],
        "occupancy": _fake_occupancy(),
    }
    return context


def get_stop_context_for_device(device):
    """
    Devuelve un contexto tipo 'stop':
    - próximas salidas desde esa parada
    - alertas
    - ocupación estimada por ruta
    """
    stop_code = device.metadata.get("stop_code", "STOP-TEC")
    stop_name = device.metadata.get("stop_name", "TEC Cartago")

    base_time = datetime.utcnow()

    upcoming_departures = []
    for i in range(5):
        dep_time = base_time + timedelta(minutes=5 * (i + 1))
        upcoming_departures.append(
            {
                "route_code": f"R-30{i+1}",
                "route_name": f"Ruta demo {i+1}",
                "destination": "Centro Cartago",
                "departure_time": dep_time.isoformat() + "Z",
                "eta_minutes": 5 * (i + 1),
                "occupancy": _fake_occupancy(),
            }
        )

    context = {
        "context_type": "stop",
        "timestamp": _now_iso(),
        "stop": {
            "code": stop_code,
            "name": stop_name,
        },
        "upcoming_departures": upcoming_departures,
        "alerts": [
            {
                "level": "warning",
                "code": "WEATHER",
                "message": "Lluvia ligera en la zona, posibles retrasos.",
            }
        ],
    }
    return context


def get_context_for_device(device):
    """
    Decide qué tipo de contexto generar según el tipo de dispositivo.
    """
    if device.device_type == device.DeviceType.ONBOARD:
        return get_onboard_context_for_device(device)
    else:
        return get_stop_context_for_device(device)
