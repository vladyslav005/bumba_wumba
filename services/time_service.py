import ntptime
import machine
import socket
import struct
import time

from config import NTP_SERVER, TIMEZONE_OFFSET_SECONDS


class TimeService:

    def sync(self, timeout_seconds=10):
        try:
            print(f"Synchronizing internet time from {NTP_SERVER}...")

            addr = socket.getaddrinfo(NTP_SERVER, 123)[0][-1]
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(timeout_seconds)

            try:
                packet = bytearray(48)
                packet[0] = 0x1B
                s.sendto(packet, addr)
                data, _ = s.recvfrom(48)
            finally:
                s.close()

            if len(data) < 48:
                raise ValueError("Invalid NTP response")

            seconds = struct.unpack(">I", data[40:44])[0] - 2208988800
            tm = time.gmtime(seconds)
            rtc = machine.RTC()
            rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))

            print("Time synchronized")
            return True

        except Exception as error:
            print("Time sync failed:", error)
            return False

    def get_time(self):
        return time.localtime(time.time() + TIMEZONE_OFFSET_SECONDS)

    def get_formatted_time(self):
        current = self.get_time()

        year = current[0]
        month = current[1]
        day = current[2]
        hour = current[3]
        minute = current[4]
        second = current[5]

        return "{:02d}.{:02d}.{:04d} {:02d}:{:02d}:{:02d}".format(
            day,
            month,
            year,
            hour,
            minute,
            second
        )