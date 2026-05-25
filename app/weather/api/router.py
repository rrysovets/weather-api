from rest_framework.routers import DefaultRouter
from weather.api.views import WeatherViewSet

router = DefaultRouter()
router.register(r"weather", WeatherViewSet, basename="weather")

urlpatterns = router.urls