from app import App
from config import WIFI_SSID, WIFI_PASSWORD

from services.ccs811_service import CCS811Service
from services.dht_service import DHTService
from services.display_service import DisplayService
from services.ir_service import IRService
from services.persistence_service import PersistenceService
from services.rgb_service import RGBService
from services.screen_navigator import ScreenNavigator
from services.telemetry_service import TelemetryService
from services.wifi_service import WiFiService

from services.time_service import TimeService

from states.air_quality_state import AirQualityState
from states.boot_state import BootState
from states.climate_state import ClimateState
from states.home_state import HomeState
from states.wifi_info_state import WifiInfoState

from config import (
    INFLUX_HOST,
    INFLUX_PORT,
    INFLUX_ORG,
    INFLUX_BUCKET,
    INFLUX_TOKEN
)

wifi_service = WiFiService(
    WIFI_SSID,
    WIFI_PASSWORD
)

time_service = TimeService()

display_service = DisplayService()

dht_service = DHTService(pin=17)

ir_service = IRService(pin=15)

ccs811_service = CCS811Service()

rgb_service = RGBService()



persistence_service = PersistenceService(
    host=INFLUX_HOST,
    port=INFLUX_PORT,
    org=INFLUX_ORG,
    bucket=INFLUX_BUCKET,
    token=INFLUX_TOKEN
)

telemetry_service = TelemetryService(
    dht_service=dht_service,
    air_service=ccs811_service,
    persistence_service=persistence_service,
    interval_ms=30000
)

screen_navigator = ScreenNavigator([
    HomeState,
    ClimateState,
    AirQualityState,
    WifiInfoState
])


app = App(
    wifi_service=wifi_service,
    time_service=time_service,
    display_service=display_service,
    dht_service=dht_service,
    ir_service=ir_service,
    screen_navigator=screen_navigator,
    ccs811_service=ccs811_service,
    rgb_service=rgb_service,
    telemetry_service=telemetry_service
)



app.change_state(BootState())

app.run()