import socket
import time
import machine
import network

from states.base_state import BaseState
import config


AP_SSID = "SuperBumba-Setup"
AP_PASSWORD = "00000000"
AP_IP = "192.168.4.1"

EXIT_BUTTON_PIN = 21
EXIT_HOLD_MS = 2000


class ConfigurationState(BaseState):

    def __init__(self, previous_state=None):
        self.previous_state = previous_state

        self.ap = None
        self.server_socket = None

        self.button_pin = None
        self.last_pin_value = 1
        self.button_pressed_at = None

        self.exit_requested = False

    # =========================================================
    # STATE
    # =========================================================

    def enter(self, app):
        self.exit_requested = False
        self.button_pressed_at = None

        app.display.show(
            "Starting setup",
            "Please wait..."
        )

        if not self._start_access_point():

            app.display.show(
                "AP ERROR",
                "Check console"
            )

            return

        self._start_server()
        self._setup_exit_button()

        if self.server_socket is not None:

            app.display.show(
                AP_SSID[:16],
                AP_IP
            )

        else:

            app.display.show(
                "SERVER ERROR",
                "Check console"
            )

    def update(self, app):

        if self.exit_requested:
            self._exit_to_previous_state(app)
            return

        self._handle_exit_button()

        if self.server_socket is None:
            return

        try:

            conn, _ = self.server_socket.accept()

        except Exception:
            return

        self._serve_client(
            app,
            conn
        )

    def exit(self, app):

        if self.server_socket is not None:

            try:
                self.server_socket.close()
            except Exception:
                pass

            self.server_socket = None

        if self.ap is not None:

            try:
                self.ap.active(False)
            except Exception:
                pass

            self.ap = None

        self.button_pin = None
        self.button_pressed_at = None
        self.exit_requested = False

    # =========================================================
    # ACCESS POINT
    # =========================================================

    def _get_ap_interface(self):

        # MicroPython 1.23+
        ap_if = getattr(
            network.WLAN,
            "IF_AP",
            None
        )

        # Older MicroPython fallback
        if ap_if is None:
            ap_if = getattr(
                network,
                "AP_IF",
                None
            )

        return ap_if

    def _start_access_point(self):

        try:

            print("Starting configuration AP...")

            ap_if = self._get_ap_interface()

            if ap_if is None:

                raise RuntimeError(
                    "No AP interface available"
                )

            self.ap = network.WLAN(
                ap_if
            )

            # Reset AP
            self.ap.active(False)

            time.sleep_ms(300)

            # Configure BEFORE enabling
            self._configure_access_point()

            # Enable AP
            self.ap.active(True)

            time.sleep_ms(700)

            if not self.ap.active():

                raise RuntimeError(
                    "AP did not become active"
                )

            # Static setup-network address
            self.ap.ifconfig((
                AP_IP,
                "255.255.255.0",
                AP_IP,
                "8.8.8.8"
            ))

            print(
                "Config AP active:",
                self.ap.active()
            )

            print(
                "Config AP SSID:",
                self._get_ap_ssid()
            )

            print(
                "Config AP network:",
                self.ap.ifconfig()
            )

            print(
                "Config AP password:",
                AP_PASSWORD
            )

            print(
                "Open: http://{}".format(
                    AP_IP
                )
            )

            return True

        except Exception as error:

            print(
                "Config AP error:",
                error
            )

            if self.ap is not None:

                try:
                    self.ap.active(False)
                except Exception:
                    pass

            self.ap = None

            return False

    def _configure_access_point(self):

        # Preferred MicroPython 1.23+ configuration
        security = getattr(
            network.WLAN,
            "SEC_WPA2",
            None
        )

        if security is not None:

            try:

                self.ap.config(
                    ssid=AP_SSID,
                    security=security,
                    key=AP_PASSWORD
                )

                print(
                    "AP configured with WPA2"
                )

                return

            except Exception as error:

                print(
                    "Modern AP config failed:",
                    error
                )

        # Compatibility fallback
        try:

            self.ap.config(
                ssid=AP_SSID,
                key=AP_PASSWORD
            )

            print(
                "AP configured using legacy key"
            )

            return

        except Exception:
            pass

        # Older firmware fallback
        try:

            self.ap.config(
                essid=AP_SSID,
                password=AP_PASSWORD
            )

            print(
                "AP configured using legacy API"
            )

            return

        except Exception as error:

            print(
                "Password AP config failed:",
                error
            )

        # Last-resort open AP
        print(
            "WARNING: starting OPEN configuration AP"
        )

        security_open = getattr(
            network.WLAN,
            "SEC_OPEN",
            None
        )

        if security_open is not None:

            self.ap.config(
                ssid=AP_SSID,
                security=security_open
            )

        else:

            self.ap.config(
                ssid=AP_SSID
            )

    def _get_ap_ssid(self):

        if self.ap is None:
            return None

        for key in (
            "ssid",
            "essid"
        ):

            try:
                return self.ap.config(key)

            except Exception:
                pass

        return None

    # =========================================================
    # HTTP SERVER
    # =========================================================

    def _start_server(self):

        try:

            self.server_socket = socket.socket()

            try:

                self.server_socket.setsockopt(
                    socket.SOL_SOCKET,
                    socket.SO_REUSEADDR,
                    1
                )

            except Exception:
                pass

            self.server_socket.bind(
                ("", 80)
            )

            self.server_socket.listen(1)

            self.server_socket.settimeout(
                0.1
            )

            print(
                "Config HTTP server started on port 80"
            )

        except Exception as error:

            print(
                "Config server error:",
                error
            )

            if self.server_socket is not None:

                try:
                    self.server_socket.close()
                except Exception:
                    pass

            self.server_socket = None

    # =========================================================
    # BUTTON
    # =========================================================

    def _setup_exit_button(self):

        try:

            self.button_pin = machine.Pin(
                EXIT_BUTTON_PIN,
                machine.Pin.IN,
                machine.Pin.PULL_UP
            )

            self.last_pin_value = (
                self.button_pin.value()
            )

        except Exception as error:

            print(
                "Config exit button error:",
                error
            )

            self.button_pin = None

    def _handle_exit_button(self):

        if self.button_pin is None:
            return

        try:

            value = self.button_pin.value()

        except Exception:
            return

        if value != self.last_pin_value:

            time.sleep_ms(20)

            try:
                value = self.button_pin.value()
            except Exception:
                return

        self.last_pin_value = value

        if value == 0:

            if self.button_pressed_at is None:

                self.button_pressed_at = (
                    time.ticks_ms()
                )

            elif time.ticks_diff(
                time.ticks_ms(),
                self.button_pressed_at
            ) >= EXIT_HOLD_MS:

                self.exit_requested = True

        else:

            self.button_pressed_at = None

    def _exit_to_previous_state(self, app):

        if self.previous_state is not None:

            app.change_state(
                self.previous_state
            )

        else:

            app.change_state(
                app.navigator.screens[0]()
            )

    # =========================================================
    # REQUEST HANDLING
    # =========================================================

    def _serve_client(
        self,
        app,
        conn
    ):

        try:

            conn.settimeout(1)

            request = self._read_request(
                conn
            )

            if not request:
                return

            request_line = (
                request
                .split(b"\r\n", 1)[0]
                .decode(
                    "utf-8",
                    "ignore"
                )
            )

            parts = request_line.split(" ")

            if len(parts) < 2:

                self._send_response(
                    conn,
                    self._render_page(
                        "Invalid request"
                    ),
                    "400 Bad Request"
                )

                return

            method = parts[0]

            path = (
                parts[1]
                .split("?", 1)[0]
            )

            if (
                method == "POST"
                and path == "/save"
            ):

                self._handle_save(
                    app,
                    conn,
                    request
                )

                return

            self._send_response(
                conn,
                self._render_page(
                    "Configure your device"
                )
            )

        except Exception as error:

            print(
                "Config request error:",
                error
            )

        finally:

            try:
                conn.close()
            except Exception:
                pass

    def _read_request(
        self,
        conn
    ):

        request = b""

        while b"\r\n\r\n" not in request:

            chunk = conn.recv(1024)

            if not chunk:
                break

            request += chunk

            if len(request) > 8192:

                raise ValueError(
                    "HTTP request too large"
                )

        if not request:
            return b""

        header, separator, body = (
            request.partition(
                b"\r\n\r\n"
            )
        )

        if not separator:
            return request

        content_length = (
            self._get_content_length(
                header
            )
        )

        while len(body) < content_length:

            chunk = conn.recv(
                min(
                    1024,
                    content_length - len(body)
                )
            )

            if not chunk:
                break

            body += chunk

        return (
            header
            + b"\r\n\r\n"
            + body
        )

    def _get_content_length(
        self,
        header
    ):

        for line in header.split(
            b"\r\n"
        ):

            if line.lower().startswith(
                b"content-length:"
            ):

                try:

                    return int(
                        line
                        .split(
                            b":",
                            1
                        )[1]
                        .strip()
                    )

                except Exception:

                    return 0

        return 0

    # =========================================================
    # SAVE CONFIG
    # =========================================================

    def _handle_save(
        self,
        app,
        conn,
        request
    ):

        _, _, body = (
            request.partition(
                b"\r\n\r\n"
            )
        )

        values = self._parse_form(
            body
        )

        current = config.get_config()

        try:

            influx_port = int(
                values.get(
                    "influx_port",
                    current.get(
                        "influx_port",
                        8086
                    )
                )
            )

            if (
                influx_port < 1
                or influx_port > 65535
            ):

                raise ValueError()

        except Exception:

            self._send_response(
                conn,
                self._render_page(
                    "Invalid InfluxDB port"
                ),
                "400 Bad Request"
            )

            return

        wifi_password = values.get(
            "wifi_password",
            ""
        )

        influx_token = values.get(
            "influx_token",
            ""
        )

        # Empty secret field = keep old value
        if not wifi_password:

            wifi_password = current.get(
                "wifi_password",
                ""
            )

        if not influx_token:

            influx_token = current.get(
                "influx_token",
                ""
            )

        config.save_config({

            "wifi_ssid":
                values.get(
                    "wifi_ssid",
                    current.get(
                        "wifi_ssid",
                        ""
                    )
                ),

            "wifi_password":
                wifi_password,

            "influx_host":
                values.get(
                    "influx_host",
                    current.get(
                        "influx_host",
                        ""
                    )
                ),

            "influx_port":
                influx_port,

            "influx_org":
                values.get(
                    "influx_org",
                    current.get(
                        "influx_org",
                        ""
                    )
                ),

            "influx_bucket":
                values.get(
                    "influx_bucket",
                    current.get(
                        "influx_bucket",
                        ""
                    )
                ),

            "influx_token":
                influx_token
        })

        app.display.show(
            "Saved",
            "Restarting..."
        )

        self._send_response(
            conn,
            self._render_page(
                "Saved successfully. Restarting..."
            )
        )

        time.sleep_ms(500)

        machine.reset()

    # =========================================================
    # FORM DECODING
    # =========================================================

    def _parse_form(
        self,
        body
    ):

        values = {}

        text = body.decode(
            "utf-8",
            "ignore"
        )

        for part in text.split("&"):

            if "=" not in part:
                continue

            key, value = part.split(
                "=",
                1
            )

            values[
                self._url_decode(key)
            ] = self._url_decode(value)

        return values

    def _url_decode(
        self,
        value
    ):

        raw = value.encode(
            "utf-8"
        )

        output = bytearray()

        i = 0

        while i < len(raw):

            current = raw[i]

            # +
            if current == 43:

                output.append(32)

                i += 1

                continue

            # %
            if (
                current == 37
                and i + 2 < len(raw)
            ):

                try:

                    hex_text = bytes([
                        raw[i + 1],
                        raw[i + 2]
                    ]).decode()

                    output.append(
                        int(
                            hex_text,
                            16
                        )
                    )

                    i += 3

                    continue

                except Exception:
                    pass

            output.append(
                current
            )

            i += 1

        return output.decode(
            "utf-8",
            "replace"
        )

    # =========================================================
    # HTML
    # =========================================================

    def _html_escape(
        self,
        value
    ):

        return (
            str(value)
            .replace(
                "&",
                "&amp;"
            )
            .replace(
                "<",
                "&lt;"
            )
            .replace(
                ">",
                "&gt;"
            )
            .replace(
                '"',
                "&quot;"
            )
            .replace(
                "'",
                "&#39;"
            )
        )

    def _render_page(
        self,
        message
    ):

        current = config.get_config()

        html = """
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>
Super Bumba Configuration
</title>

<style>

:root {{
    color-scheme: dark;
}}

body {{
    font-family: Arial, sans-serif;
    margin: 0;

    background:
        linear-gradient(
            135deg,
            #07111f,
            #173a5e
        );

    color: #f5f8ff;

    min-height: 100vh;

    display: flex;

    align-items: center;
    justify-content: center;

    padding: 20px;

    box-sizing: border-box;
}}

.card {{
    width: min(100%, 720px);

    background:
        rgba(
            8,
            20,
            35,
            0.95
        );

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.14
        );

    border-radius: 20px;

    padding: 24px;
}}

h1 {{
    margin-top: 0;
    color: #7ee7ff;
}}

p {{
    line-height: 1.5;
}}

.row {{
    display: grid;

    gap: 8px;

    margin-bottom: 14px;
}}

label {{
    font-weight: 600;
}}

input {{
    width: 100%;

    padding: 12px 14px;

    border-radius: 10px;

    border:
        1px solid
        #3f5872;

    background: #0f2239;

    color: white;

    box-sizing: border-box;
}}

button {{
    background:
        linear-gradient(
            135deg,
            #1fb6b8,
            #2f7fe0
        );

    border: none;

    border-radius: 999px;

    color: white;

    padding: 12px 18px;

    font-size: 16px;

    font-weight: 700;

    cursor: pointer;

    margin-top: 8px;
}}

.hint {{
    color: #8dc5ff;

    font-size: 0.95rem;
}}

.status {{
    color: #98ffbf;

    font-weight: 600;
}}

</style>

</head>

<body>

<div class="card">

<h1>
Super Bumba Setup
</h1>

<p class="status">
{message}
</p>

<p>
Connect to
<strong>{ap_ssid}</strong>,
then open
<strong>http://{ap_ip}</strong>.
</p>

<form
    method="post"
    action="/save"
>

<div class="row">

<label for="wifi_ssid">
Wi-Fi SSID
</label>

<input
    id="wifi_ssid"
    name="wifi_ssid"
    value="{wifi_ssid}"
    required
>

</div>


<div class="row">

<label for="wifi_password">
Wi-Fi Password
</label>

<input
    id="wifi_password"
    name="wifi_password"
    type="password"
    placeholder="Leave blank to keep current password"
>

</div>


<div class="row">

<label for="influx_host">
InfluxDB Host
</label>

<input
    id="influx_host"
    name="influx_host"
    value="{influx_host}"
    required
>

</div>


<div class="row">

<label for="influx_port">
InfluxDB Port
</label>

<input
    id="influx_port"
    name="influx_port"
    type="number"
    min="1"
    max="65535"
    value="{influx_port}"
    required
>

</div>


<div class="row">

<label for="influx_org">
InfluxDB Org
</label>

<input
    id="influx_org"
    name="influx_org"
    value="{influx_org}"
    required
>

</div>


<div class="row">

<label for="influx_bucket">
InfluxDB Bucket
</label>

<input
    id="influx_bucket"
    name="influx_bucket"
    value="{influx_bucket}"
    required
>

</div>


<div class="row">

<label for="influx_token">
InfluxDB Token
</label>

<input
    id="influx_token"
    name="influx_token"
    type="password"
    placeholder="Leave blank to keep current token"
>

</div>


<button type="submit">
Save and restart
</button>

</form>


<p class="hint">

Setup network:
<strong>{ap_ssid}</strong>

<br>

Setup password:
<strong>{ap_password}</strong>

<br>

Configuration address:
<strong>http://{ap_ip}</strong>

<br><br>

Hold GP21 for 2 seconds
to leave configuration mode.

</p>

</div>

</body>

</html>
"""

        return html.format(

            message=
                self._html_escape(
                    message
                ),

            wifi_ssid=
                self._html_escape(
                    current.get(
                        "wifi_ssid",
                        ""
                    )
                ),

            influx_host=
                self._html_escape(
                    current.get(
                        "influx_host",
                        ""
                    )
                ),

            influx_port=
                self._html_escape(
                    current.get(
                        "influx_port",
                        8086
                    )
                ),

            influx_org=
                self._html_escape(
                    current.get(
                        "influx_org",
                        ""
                    )
                ),

            influx_bucket=
                self._html_escape(
                    current.get(
                        "influx_bucket",
                        ""
                    )
                ),

            ap_ssid=
                self._html_escape(
                    AP_SSID
                ),

            ap_password=
                self._html_escape(
                    AP_PASSWORD
                ),

            ap_ip=
                self._html_escape(
                    AP_IP
                )
        )

    # =========================================================
    # HTTP RESPONSE
    # =========================================================

    def _send_response(
        self,
        conn,
        body,
        status="200 OK"
    ):

        body_bytes = body.encode(
            "utf-8"
        )

        header = (
            "HTTP/1.1 {}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).format(
            status,
            len(body_bytes)
        )

        conn.sendall(
            header.encode(
                "utf-8"
            )
        )

        conn.sendall(
            body_bytes
        )