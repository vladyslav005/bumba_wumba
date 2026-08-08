"""Configuration values for the Super Bumba firmware application."""

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