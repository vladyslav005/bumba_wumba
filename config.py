"""Configuration values for the Super Bumba firmware application."""

import json

WIFI_SSID = "ASUS-UB"
WIFI_PASSWORD = "00000000"
DISPLAY_BRIGHTNESS = 128
TIME_SYNC_INTERVAL_SECONDS = 60
NTP_SERVER = "0.sk.pool.ntp.org"
TIMEZONE_OFFSET_SECONDS = 2 * 60 * 60  # UTC+2

INFLUX_HOST = "10.42.0.1"   # replace with your Ubuntu IP
INFLUX_PORT = 8086

INFLUX_ORG = "super-bumba"
INFLUX_BUCKET = "sensors"

INFLUX_TOKEN = "super-bumba-pico-secret-token-2026"

CONFIG_FILE = "config.json"


def _load_from_file():
    try:
        with open(CONFIG_FILE, "r") as handle:
            data = json.load(handle)
            return data
    except Exception:
        return {}


def _write_to_file(data):
    try:
        with open(CONFIG_FILE, "w") as handle:
            json.dump(data, handle)
    except Exception as error:
        print("Config write error:", error)


for key, value in _load_from_file().items():
    if key == "wifi_ssid":
        WIFI_SSID = value
    elif key == "wifi_password":
        WIFI_PASSWORD = value
    elif key == "influx_host":
        INFLUX_HOST = value
    elif key == "influx_port":
        INFLUX_PORT = int(value)
    elif key == "influx_org":
        INFLUX_ORG = value
    elif key == "influx_bucket":
        INFLUX_BUCKET = value
    elif key == "influx_token":
        INFLUX_TOKEN = value


def get_config():
    return {
        "wifi_ssid": WIFI_SSID,
        "wifi_password": WIFI_PASSWORD,
        "influx_host": INFLUX_HOST,
        "influx_port": INFLUX_PORT,
        "influx_org": INFLUX_ORG,
        "influx_bucket": INFLUX_BUCKET,
        "influx_token": INFLUX_TOKEN,
    }


def save_config(values):
    global WIFI_SSID, WIFI_PASSWORD, INFLUX_HOST, INFLUX_PORT, INFLUX_ORG, INFLUX_BUCKET, INFLUX_TOKEN

    WIFI_SSID = values.get("wifi_ssid", WIFI_SSID)
    WIFI_PASSWORD = values.get("wifi_password", WIFI_PASSWORD)
    INFLUX_HOST = values.get("influx_host", INFLUX_HOST)
    INFLUX_PORT = int(values.get("influx_port", INFLUX_PORT))
    INFLUX_ORG = values.get("influx_org", INFLUX_ORG)
    INFLUX_BUCKET = values.get("influx_bucket", INFLUX_BUCKET)
    INFLUX_TOKEN = values.get("influx_token", INFLUX_TOKEN)

    _write_to_file(get_config())