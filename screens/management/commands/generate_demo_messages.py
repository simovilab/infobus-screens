from django.core.management.base import BaseCommand

from screens.models import Device, ScreenTemplate, DeviceMessage
from screens.infobus_client import get_context_for_device


class Command(BaseCommand):
    help = "Genera mensajes de demostración para todos los dispositivos activos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--device-id",
            type=str,
            help="Si se indica, solo genera mensajes para este dispositivo (UUID).",
        )

    def handle(self, *args, **options):
        device_id = options.get("device_id")

        if device_id:
            devices = Device.objects.filter(id=device_id, is_active=True)
        else:
            devices = Device.objects.filter(is_active=True)

        if not devices.exists():
            self.stdout.write(self.style.WARNING("No hay dispositivos activos."))
            return

        for device in devices:
            context = get_context_for_device(device)
            if not context:
                self.stdout.write(
                    self.style.WARNING(f"Sin contexto para dispositivo {device}")
                )
                continue

            # Elegir template: primero device.screen_template, si no, uno por contexto
            template = device.screen_template

            if not template:
                context_type = context.get("context_type")
                # Buscar un template que haga match con el contexto
                template = (
                    ScreenTemplate.objects.filter(
                        context=context_type,
                        is_active=True,
                    )
                    .order_by("id")
                    .first()
                )

            if not template:
                self.stdout.write(
                    self.style.WARNING(
                        f"Sin template para dispositivo {device} (tipo {device.device_type})"
                    )
                )
                continue

            msg = DeviceMessage.objects.create(
                device=device,
                template=template,
                payload=context,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Creado DeviceMessage {msg.id} para {device.name} ({device.device_type})"
                )
            )
