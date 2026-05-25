from django.db import models
from django.utils import timezone


class WeatherRequest(models.Model):
    class Units(models.TextChoices):
        CELSIUS = "celsius", "Celsius"
        FAHRENHEIT = "fahrenheit", "Fahrenheit"

    city = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    temperature = models.FloatField()
    feels_like = models.FloatField()
    description = models.TextField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    units = models.CharField(max_length=10, choices=Units.choices)
    from_cache = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.city} at {self.timestamp}"
