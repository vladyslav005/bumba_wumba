from app import App
from config import WIFI_SSID, WIFI_PASSWORD

from services.display_service import DisplayService
from services.wifi_service import WiFiService

from services.time_service import TimeService

from states.boot_state import BootState


wifi_service = WiFiService(
    WIFI_SSID,
    WIFI_PASSWORD
)

time_service = TimeService()

display_service = DisplayService()

app = App(
    wifi_service=wifi_service,
    time_service=time_service,
    display_service=display_service
)

app.change_state(BootState())

app.run()