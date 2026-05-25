from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from weather.services.weather_services import WeatherService


class WeatherCacheTest(TestCase):

    @patch("weather.services.weather_services.cache.get")
    @patch("weather.services.weather_services.cache.set")
    @patch("weather.services.weather_services.WeatherApiService.get_weather")
    def test_cache_is_used_instead_of_api(self, mock_api, mock_cache_set, mock_cache_get):

        cached_value = {
            "city": "Riga",
            "temperature": 10,
            "feels_like": 8,
            "description": "clear",
            "humidity": 50,
            "wind_speed": 3,
            "units": "celsius",
        }

        mock_cache_get.side_effect = [None, cached_value]

        mock_api.return_value = {
            "city": "Riga",
            "temperature": 10,
            "feels_like": 8,
            "description": "clear",
            "humidity": 50,
            "wind_speed": 3,
        }

        service = WeatherService()

        result1 = service.get_weather("Riga", "celsius")
        result2 = service.get_weather("Riga", "celsius")
        
        self.assertEqual(mock_api.call_count, 1)
        self.assertEqual(mock_cache_get.call_count, 2)
        self.assertEqual(mock_cache_set.call_count, 1)

        self.assertFalse(result1["from_cache"])
        self.assertTrue(result2["from_cache"])
                
        

class RateLimitTest(APITestCase):

    def test_rate_limit_returns_429(self):
        url = "/api/weather/"

        responses = []
        for _ in range(40):
            responses.append(self.client.get(url))

        self.assertIn(
            status.HTTP_429_TOO_MANY_REQUESTS,
            [r.status_code for r in responses]
        )
        
        
class PaginationTest(APITestCase):

    def test_pagination_structure(self):
        response = self.client.get("/api/weather/?page=1")

        self.assertEqual(response.status_code, 200)

        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)


    def test_filter_by_city(self):
        response = self.client.get("/api/weather/?city=Riga")

        self.assertEqual(response.status_code, 200)

        for item in response.data["results"]:
            self.assertEqual(item["city"], "Riga")
            
    def test_filter_by_date_from(self):
        response = self.client.get("/api/weather/?date_from=2026-01-01T00:00:00Z")

        self.assertEqual(response.status_code, 200)

        for item in response.data["results"]:
            self.assertGreaterEqual(item["timestamp"], "2026-01-01T00:00:00Z")