import ntptime
import time

from config import NTP_SERVER, TIMEZONE_OFFSET_SECONDS


class TimeService:

    def sync(self):
        try:
            print(f"Synchronizing internet time from {NTP_SERVER}...")

            ntptime.host = NTP_SERVER
            ntptime.settime()

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