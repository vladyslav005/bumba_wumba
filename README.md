# Super Bumba

Firmware and telemetry stack for a Raspberry Pi Pico W air quality monitor with InfluxDB and Grafana.

## Overview

This repository contains:
- MicroPython firmware for a Pico W device that reads:
  - CCS811 air quality sensor (eCO2 and TVOC)
  - DHT temperature/humidity sensor
- RGB LED status updates based on air quality
- Wi-Fi connection and automatic reconnect support
- Persistence to InfluxDB
- Grafana dashboard provisioning for visualizing sensor data

## Requirements

### Hardware
- Raspberry Pi Pico W
- CCS811 air quality sensor
- DHT temperature/humidity sensor
- NeoPixel / WS2812 RGB LED
- Display module supported by `services/display_service.py`
- IR receiver and / or navigation button hardware

### Software
- MicroPython firmware installed on the Pico W
- `mpremote` for deploying firmware
- Docker and Docker Compose for InfluxDB + Grafana

## Configuration

1. Open `config.py` and update network and persistence settings:
   - `WIFI_SSID`
   - `WIFI_PASSWORD`
   - `INFLUX_HOST`
   - `INFLUX_PORT`
   - `INFLUX_ORG`
   - `INFLUX_BUCKET`
   - `INFLUX_TOKEN`

2. Ensure the Pico W and the InfluxDB host are on the same network.
   - If using Docker on a laptop, the Pico must be able to reach the host IP configured in `INFLUX_HOST`.
   - `INFLUX_HOST` should be the host IP visible to the Pico, not `localhost`.

3. Create `server/.env` from `server/.env.example` and set the following values:
   - `INFLUX_USERNAME`
   - `INFLUX_PASSWORD`
   - `INFLUX_ORG`
   - `INFLUX_BUCKET`
   - `INFLUX_TOKEN`
   - `GRAFANA_USER`
   - `GRAFANA_PASSWORD`

## Running the server stack

From the repository root:

```sh
cd server
cp .env.example .env
# edit .env as needed

docker compose up -d
```

- InfluxDB will be available on port `8086`.
- Grafana will be available on port `3000`.

### Grafana dashboard

The repository includes dashboard provisioning under `server/grafana/`:
- `dashboards/super-bumba.json`
- `provisioning/dashboards/dashboards.yaml`
- `provisioning/datasources/influxdb.yaml`

## Deploying the Pico W firmware

Install `mpremote` on your host machine if needed:

```sh
python3 -m pip install mpremote
```

Connect your Pico W and copy files:

```sh
mpremote connect /dev/ttyACM0 fs cp -r *.py :/
```

If necessary, first erase or delete old files on the device before copying.

Run the firmware:

```sh
mpremote connect /dev/ttyACM0 run main.py
```

## Project structure

- `main.py` — application entry point that constructs services and starts the state machine
- `app.py` — runtime loop and application state management
- `config.py` — Wi-Fi and InfluxDB configuration values
- `services/` — hardware and telemetry service implementations
- `states/` — application screen and state logic
- `server/` — InfluxDB + Grafana Docker Compose configuration and dashboard provisioning

## Notes

- Automatic Wi-Fi reconnect is handled in the telemetry and application logic.
- RGB LED colors reflect air quality after each sensor read.
- If the device loses Wi-Fi, it will retry and skip persistence until it reconnects.

## Troubleshooting

- If the Pico cannot connect to Wi-Fi, verify `config.py` credentials and signal strength.
- If data does not reach InfluxDB, confirm the Pico can reach `INFLUX_HOST` and that your token is valid.
- Use Grafana at `http://localhost:3000` to verify that the dashboard loads and data is being written.
