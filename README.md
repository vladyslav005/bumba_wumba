# Super Bumba

Firmware and telemetry stack for a Raspberry Pi Pico W air quality monitor with InfluxDB and Grafana.

## Overview

This repository contains a MicroPython firmware project for a Pico W device that:
- reads CCS811 air quality data (eCO2 and TVOC)
- reads DHT temperature and humidity
- drives an RGB NeoPixel LED to show air quality
- displays status on an I2C LCD
- connects to Wi-Fi and writes telemetry to InfluxDB
- provides a web-based config portal on the Pico W
- includes Grafana provisioning for dashboarding

## What you need

### Hardware
- Raspberry Pi Pico W
- CCS811 air quality sensor
- DHT11 or DHT22 temperature/humidity sensor
- I2C LCD display with a PCF8574 backpack (commonly a 16x2 display)
- WS2812 / NeoPixel RGB LED (1 pixel)
- IR receiver module for remote control
- Optional push buttons for local navigation and config mode
- Wires, breadboard, and a shared ground connection

### Software
- MicroPython firmware for Pico W
- `mpremote` to deploy files to the Pico W
- Docker and Docker Compose for InfluxDB + Grafana
- A browser to access the Pico config portal and Grafana

## Pin mapping and wiring

### Pico W pin assignments used by the firmware

- `GP26` — CCS811 SDA
- `GP27` — CCS811 SCL
- `GP4`  — LCD SDA
- `GP5`  — LCD SCL
- `GP17` — DHT data pin
- `GP15` — IR receiver output
- `GP28` — NeoPixel LED data
- `GP20` — local "next screen" button
- `GP22` — local "previous screen" button (and retry on Wi-Fi error)
- `GP21` — hold for 2 seconds to enter Pico config AP / exit config mode

### General wiring notes

- All modules must share the same ground with the Pico W.
- The CCS811 and LCD are I2C devices; wire them both to the Pico's I2C pins plus power.
- The NeoPixel expects 3.3V data from the Pico GPIO; power it from 3.3V and ground.
- The DHT sensor should be powered from 3.3V and connected to `GP17`.
- The IR receiver output connects to `GP15`.
- Use pull-up or pull-down buttons to `GP20`, `GP22`, and `GP21` if you want physical navigation controls.

## Software setup from scratch

### 1. Prepare the host environment

1. Install Docker and Docker Compose.
2. Install `mpremote` on your computer:

```sh
python3 -m pip install mpremote
```

### 2. Configure the server stack

1. Copy the example environment file:

```sh
cd server
cp .env.example .env
```

2. Edit `server/.env` with your desired InfluxDB and Grafana settings.

3. Start InfluxDB and Grafana:

```sh
docker compose up -d
```

4. Confirm InfluxDB is reachable at the host IP and port you will configure on the Pico.

### 3. Configure the Pico network and persistence settings

There are two ways to set the Pico Wi-Fi and persistence values:

#### Option A: Edit `config.py` directly before flashing

Open `config.py` and set:
- `WIFI_SSID`
- `WIFI_PASSWORD`
- `INFLUX_HOST`
- `INFLUX_PORT`
- `INFLUX_ORG`
- `INFLUX_BUCKET`
- `INFLUX_TOKEN`

Make sure `INFLUX_HOST` is the host IP visible to the Pico, not `localhost`.

#### Option B: Use the Pico config portal after boot

1. Boot the Pico W firmware.
2. Hold `GP21` for 2 seconds while the device is running.
3. The Pico will start an access point named `SuperBumba`.
4. Connect your computer or phone to that access point.
5. Open a browser and go to `http://192.168.4.1`.
6. Enter your Wi-Fi SSID/password and InfluxDB settings.
7. Save and allow the Pico to restart.

> The default config AP password is `00000000`.

### 4. Flash the Pico W firmware

From the repository root:

```sh
mpremote connect /dev/ttyACM0 fs cp -r *.py :/
```

If the Pico already contains old code, remove or overwrite it before copying.

Run the firmware:

```sh
mpremote connect /dev/ttyACM0 run main.py
```

### 5. Verify operation

- The Pico should boot and attempt Wi-Fi connection.
- The display should show startup and then cycle through screen content.
- The Pico should send telemetry to InfluxDB if Wi-Fi connects.
- Open Grafana at `http://localhost:3000` and verify the dashboard.

## Controls and navigation

### IR remote
- `FORWARD` button moves to the next screen
- `BACK` button moves to the previous screen

### Local buttons
- `GP20` — next screen
- `GP22` — previous screen
- `GP21` — hold for 2 seconds to enter config portal / exit config mode

### Wi-Fi error retry
- When a Wi-Fi failure screen appears, press the `GP22` button to retry connection.

## Screen behavior

- **Boot**: startup message while the device initializes
- **Home**: current time/date display
- **Climate**: temperature and humidity from the DHT sensor
- **Air Quality**: eCO2 and TVOC values from the CCS811 sensor, plus RGB status
- **WiFi Info**: connection status and IP address

## Recommended component checklist

- Raspberry Pi Pico W board
- CCS811 air quality sensor module
- DHT11 or DHT22 sensor
- I2C LCD display module
- WS2812 / NeoPixel RGB LED
- IR receiver (e.g. TSOP38238)
- Three push buttons for local screen/config control
- Appropriate jumper wires, breadboard, and power supply

## Troubleshooting

- If you cannot connect to Wi-Fi, double-check the SSID/password and the Pico's position relative to the router.
- If the config portal is not reachable, hold `GP21` for 2 seconds and verify the AP named `SuperBumba` appears.
- If the Pico still shows the wrong Wi-Fi credentials, use the browser portal to re-enter them and restart.
- If InfluxDB data is not received, verify `INFLUX_HOST` is the reachable host IP from the Pico.
- Check Grafana at `http://localhost:3000` to ensure the dashboard is provisioned and connecting to InfluxDB.

## Project structure

- `main.py` — application entry point that constructs services and starts the state machine
- `app.py` — runtime loop and application state management
- `config.py` — Wi-Fi and InfluxDB configuration values
- `services/` — hardware and telemetry service implementations
- `states/` — application screen and state logic
- `server/` — InfluxDB + Grafana Docker Compose configuration and dashboard provisioning
