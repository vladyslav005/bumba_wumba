import socket


class PersistenceService:

    def __init__(
        self,
        host,
        port,
        org,
        bucket,
        token
    ):
        self.host = host
        self.port = port
        self.org = org
        self.bucket = bucket
        self.token = token

    def save(self, temperature, humidity, eco2, tvoc):
        body = (
            "environment,device=pico1 "
            "temperature={},"
            "humidity={},"
            "eco2={}i,"
            "tvoc={}i"
        ).format(
            temperature,
            humidity,
            eco2,
            tvoc
        )

        path = (
            "/api/v2/write"
            "?org={}"
            "&bucket={}"
            "&precision=s"
        ).format(
            self.org,
            self.bucket
        )

        request = (
            "POST {} HTTP/1.1\r\n"
            "Host: {}:{}\r\n"
            "Authorization: Token {}\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
            "{}"
        ).format(
            path,
            self.host,
            self.port,
            self.token,
            len(body),
            body
        )

        sock = None

        try:
            address = socket.getaddrinfo(
                self.host,
                self.port
            )[0][-1]

            sock = socket.socket()
            sock.connect(address)

            sock.send(request.encode())

            response = sock.recv(128)

            success = (
                b"204" in response or
                b"200" in response
            )

            if success:
                print("Reading persisted")
            else:
                print("InfluxDB response:", response)

            return success

        except Exception as error:
            print("Persistence error:", error)
            return False

        finally:
            if sock is not None:
                sock.close()