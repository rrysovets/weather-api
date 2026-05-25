from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from weather.api.views import WeatherViewSet,HealthView

router = DefaultRouter()
router.register(prefix=r"weather", viewset=WeatherViewSet, basename="weather")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("health/", HealthView.as_view(), name="health"),
]

