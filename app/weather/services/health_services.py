import time
import logging
import requests

from django.conf import settings
from django.db import connection
from django.core.cache import cache

logger = logging.getLogger("weather")


class HealthCheckService:

    def check_db(self) -> dict:
        start = time.perf_counter()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            latency = time.perf_counter() - start
            return {
                "db": "ok",
                "db_latency_ms": round(latency * 1000, 2),
            }
        except Exception as e:
            logger.error(f"health_db_failed error={e}")
            return {"db": "fail"}

    def check_cache(self) -> dict:
        start = time.perf_counter()

        try:
            cache.set("health", "1", timeout=1)
            cache.get("health")

            latency = time.perf_counter() - start

            return {
                "cache": "ok",
                "cache_latency_ms": round(latency * 1000, 2),
            }
        except Exception as e:
            logger.warning(f"health_cache_failed error={e}")
            return {"cache": "fail"}

    def check_external_api(self) -> dict:
        start = time.perf_counter()
        try:
            response = requests.get(
                settings.WEATHER_API_BASE_URL,
                params={
                    "q": "London",
                    "appid": settings.WEATHER_API_KEY,
                },
                timeout=3,
            )
            response.raise_for_status()
            latency = time.perf_counter() - start
            return {
                "external_api": "ok",
                "api_latency_ms": round(latency * 1000, 2),
                "status_code": response.status_code,
            }

        except Exception as e:
            logger.error(f"health_api_failed error={e}")
            return {"external_api": "fail"}

    def get_health(self) -> dict:
        logger.info("health_check_started")

        result = {
            **self.check_db(),
            **self.check_cache(),
            **self.check_external_api(),
        }

        logger.info(f"health_check_finished result={result}")

        return result
