from config import (
    INFLUX_HOST,
    INFLUX_PORT,
    INFLUX_ORG,
    INFLUX_BUCKET,
    INFLUX_TOKEN
)

from services.wifi_service import WiFiService
from services.persistence_service import PersistenceService

from config import WIFI_SSID, WIFI_PASSWORD


wifi = WiFiService(
    WIFI_SSID,
    WIFI_PASSWORD
)

if wifi.connect():

    persistence = PersistenceService(
        INFLUX_HOST,
        INFLUX_PORT,
        INFLUX_ORG,
        INFLUX_BUCKET,
        INFLUX_TOKEN
    )

    persistence.save(
        temperature=25.3,
        humidity=51,
        eco2=710,
        tvoc=42
    )