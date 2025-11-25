import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class DeviceGroup(models.Model):
    class GroupType(models.TextChoices):
        ROUTE = "route", "Route"
        TERMINAL = "terminal", "Terminal"
        ZONE = "zone", "Zone"
        CUSTOM = "custom", "Custom"

    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional code (e.g., route ID, terminal code, zone code).",
    )
    group_type = models.CharField(
        max_length=20,
        choices=GroupType.choices,
        default=GroupType.CUSTOM,
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.group_type})"
    
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Default env vars for devices in this group.",
    )

    def __str__(self):
        return f"{self.name} ({self.group_type})"

class Device(models.Model):
    class DeviceType(models.TextChoices):
        ONBOARD = "onboard", "On-board"
        STOP = "stop", "Stop"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=120)
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.ONBOARD,
    )
    group = models.ForeignKey(
        DeviceGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
    )
    auth_token = models.CharField(
        max_length=64,
        unique=True,
        help_text="Token used by the device to authenticate.",
    )
    is_active = models.BooleanField(default=True)

    screen_template = models.ForeignKey(
        "ScreenTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="devices",
        help_text="Template that this device should use by default.",
    )

    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-device env vars and overrides.",
    )

    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Arbitrary device info (firmware, resolution, etc.).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} [{self.device_type}]"

class DistributionChannel(models.Model):
    """
    Logical channel to group which content goes to which devices.
    E.g. 'Route 3 - Northbound', 'Terminal A', 'Test devices'.
    """

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    groups = models.ManyToManyField(
        DeviceGroup,
        blank=True,
        related_name="channels",
    )
    devices = models.ManyToManyField(
        Device,
        blank=True,
        related_name="channels",
    )

    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Env vars/layout applied to devices in this channel.",
    )

    default_template = models.ForeignKey(
        "ScreenTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="channels_default",
        help_text="Default template for devices in this channel.",
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ScreenTemplate(models.Model):
    class TemplateContext(models.TextChoices):
        ONBOARD = "onboard", "On-board"
        STOP = "stop", "Stop"

    name = models.CharField(max_length=120)
    code = models.CharField(
        max_length=80,
        unique=True,
        help_text="Template identifier used by devices/config.",
    )
    context = models.CharField(
        max_length=20,
        choices=TemplateContext.choices,
        default=TemplateContext.ONBOARD,
    )
    description = models.TextField(blank=True)

    # Para el proyecto vamos a guardar el layout directamente como texto.
    html = models.TextField(help_text="Base HTML layout.")
    css = models.TextField(blank=True, help_text="Optional CSS for the layout.")
    js = models.TextField(blank=True, help_text="Optional JS for the layout.")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.context})"

class DeviceMessage(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In progress"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.BigAutoField(primary_key=True)
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    channel = models.ForeignKey(
        DistributionChannel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="messages",
    )
    template = models.ForeignKey(
        ScreenTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="messages",
    )

    payload = models.JSONField(
        help_text="Rendered data for the screen (e.g. next stops, timetable, alerts).",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=5)

    last_attempt_at = models.DateTimeField(null=True, blank=True)
    next_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this message should be retried (for backoff).",
    )
    delivered_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=("device", "status", "next_attempt_at")),
        ]

    def __str__(self):
        return f"Msg {self.id} → {self.device} [{self.status}]"
    
@receiver(post_save, sender=DeviceMessage)
def device_message_post_save(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza un DeviceMessage, si está en estado 'pending',
    se intenta mandarlo en tiempo real al dispositivo.
    """
    if instance.status != DeviceMessage.Status.PENDING:
        return

    from .realtime import push_device_message

    push_device_message(instance)
