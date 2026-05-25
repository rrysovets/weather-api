from rest_framework import viewsets
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework_csv.renderers import CSVRenderer

from django_filters import FilterSet, DateTimeFilter, CharFilter
from django_filters.rest_framework import DjangoFilterBackend

from weather.models import WeatherRequest
from weather.throttling import CustomAnonRateThrottle
from weather.api.serializers import WeatherRequestSerializer

from weather.services.weather_services import WeatherService
from weather.services.health_services import HealthCheckService




class WeatherFilter(FilterSet):

    city = CharFilter(lookup_expr="icontains")
    date_from = DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    date_to = DateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = WeatherRequest
        fields = ["city"]


class WeatherViewSet(viewsets.ModelViewSet):

    serializer_class = WeatherRequestSerializer
    throttle_classes = CustomAnonRateThrottle,
    filter_backends = DjangoFilterBackend,
    filterset_class = WeatherFilter
    service = WeatherService()

    def get_queryset(self):

        return WeatherRequest.objects.all().order_by("-timestamp")

    def perform_create(self, serializer):

        city = serializer.validated_data["city"]
        units = serializer.validated_data["units"]

        weather_data = self.service.get_weather(city=city,units=units,)

        if not weather_data:
            raise APIException("Failed to fetch weather data")

        serializer.save(**weather_data)

    @action(
        detail=False,
        methods=["get"],
        url_path="export-csv",
        renderer_classes=[CSVRenderer],
    )
    def export_csv(self, request):

        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        return Response(
            serializer.data,
            headers={"Content-Disposition": 'attachment; filename="weather.csv"'},
        )




class HealthView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):

        service = HealthCheckService()
        result = service.get_health()

        status_code = 200

        if "fail" in result.values():
            status_code = 503

        return Response(result, status=status_code)
