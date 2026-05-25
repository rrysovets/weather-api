
from rest_framework import serializers
from ..models import WeatherRequest

class WeatherRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRequest
        read_only_fields = (
                  'timestamp',
                  'temperature',
                  'feels_like',
                  'description',
                  'humidity',
                  'wind_speed',
                  'from_cache',)
        
        fields = [ 
                  'city',
                  'timestamp',
                  'units',
                  'temperature',
                  'feels_like',
                  'description',
                  'humidity',
                  'wind_speed',
                  'from_cache',]
        
