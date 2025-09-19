from django.contrib.gis.db import models

# Create your models here.


class DataProvider(models.Model):
    name = models.CharField(
        max_length=255, help_text="Name of the GTFS-based data provider."
    )
    sse_url = models.URLField(
        help_text="Base URL of the data provider's server-sent events."
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Designates whether this provider is the active one.",
    )

    def __str__(self):
        return self.name


class StopBase(models.Model):
    """Individual locations where vehicles pick up or drop off riders. Maps to stops.txt in the GTFS feed.

    TODO: check wheelchair_boarding choices (different for stops and stations)
    """

    WHEELCHAIR_BOARDING_CHOICES = [
        (0, "No information"),
        (1, "Accessible"),
        (2, "Not accessible"),
    ]

    stop_id = models.CharField(
        max_length=255, primary_key=True, help_text="Unique identifier for the stop."
    )
    stop_code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stop code, visible in the URL.",
    )
    stop_name = models.CharField(max_length=255, help_text="Name of the stop.")
    stop_desc = models.TextField(
        blank=True, null=True, help_text="Description of the stop."
    )
    stop_point = models.PointField(
        blank=True, null=True, help_text="Georeferenced point of the stop."
    )
    location_type = models.PositiveIntegerField(
        blank=True, null=True, help_text="Type of the location."
    )
    wheelchair_boarding = models.PositiveIntegerField(
        blank=True, null=True, choices=WHEELCHAIR_BOARDING_CHOICES
    )

    class Meta:
        abstract = True


class Station(StopBase):
    """A stop that is a station."""

    def __str__(self):
        return self.stop_name


class Stop(StopBase):
    """An individual stop or platform, typically part of a larger station."""

    STOP_HEADING_CHOICES = [
        ("N", "North"),
        ("NE", "Northeast"),
        ("E", "East"),
        ("SE", "Southeast"),
        ("S", "South"),
        ("SW", "Southwest"),
        ("W", "West"),
        ("NW", "Northwest"),
    ]
    stop_heading = models.CharField(
        max_length=2,
        choices=STOP_HEADING_CHOICES,
        blank=True,
        null=True,
        help_text="Compass direction that the vehicles arriving at the stop face.",
    )
    parent_station = models.ForeignKey(
        Station, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        if self.stop_heading:
            return f"{self.stop_id}: {self.stop_name} ({self.stop_heading})"
        return f"{self.stop_id}: {self.stop_name}"


class Vehicle(models.Model):
    """Vehicles that are used for public transit."""

    vehicle_id = models.CharField(
        max_length=255, primary_key=True, help_text="Unique identifier for the vehicle."
    )
    vehicle_label = models.CharField(
        max_length=255, blank=True, null=True, help_text="Vehicle label."
    )
    vehicle_license_plate = models.CharField(
        max_length=255, blank=True, null=True, help_text="Vehicle license plate."
    )
    vehicle_model = models.CharField(
        max_length=255, blank=True, null=True, help_text="Vehicle model."
    )
    vehicle_make = models.CharField(
        max_length=255, blank=True, null=True, help_text="Vehicle make."
    )
    vehicle_year = models.PositiveIntegerField(
        blank=True, null=True, help_text="Vehicle year."
    )
    wheelchair_accessible = models.PositiveIntegerField(
        blank=True, null=True, help_text="Wheelchair accessibility."
    )

    def __str__(self):
        return self.vehicle_label


class Screen(models.Model):
    """A screen that displays information."""

    ORIENTATION_CHOICES = [
        ("landscape", "Landscape"),
        ("portrait", "Portrait"),
    ]
    RATIO_CHOICES = [
        ("4:3", "4:3"),
        ("16:9", "16:9"),
        ("16:10", "16:10"),
    ]

    screen_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    orientation = models.CharField(
        max_length=10,
        choices=ORIENTATION_CHOICES,
        default="landscape",
        blank=True,
        null=True,
    )
    ratio = models.CharField(
        max_length=10, choices=RATIO_CHOICES, default="16:9", blank=True, null=True
    )
    size = models.PositiveIntegerField(
        help_text="diagonal in inches", blank=True, null=True
    )
    has_audio = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        abstract = True


class StopScreen(Screen):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    stop_slug = models.SlugField(unique=True)
    # TODO: fields for heading and for screen layout

    def __str__(self):
        if self.stop.stop_heading:
            return (
                f"{self.stop.stop_name} ({self.stop.stop_heading}) ({self.screen_id})"
            )
        else:
            return f"{self.stop.stop_name} ({self.screen_id})"


class StationScreen(Screen):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    station_slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.station.stop_name} ({self.screen_id})"


class VehicleScreen(Screen):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    vehicle_slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.vehicle.vehicle_label} ({self.screen_id})"
