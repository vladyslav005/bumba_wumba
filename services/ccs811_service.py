from machine import Pin, I2C
import time


class CCS811Service:

    ADDRESS = 0x5A

    STATUS = 0x00
    MEAS_MODE = 0x01
    ALG_RESULT_DATA = 0x02
    HW_ID = 0x20
    APP_START = 0xF4

    def __init__(
        self,
        sda_pin=26,
        scl_pin=27,
        address=ADDRESS
    ):
        self.address = address

        self.i2c = I2C(
            1,
            sda=Pin(sda_pin),
            scl=Pin(scl_pin),
            freq=100000
        )

        self._initialize()

    def _initialize(self):
        print("Initializing CCS811...")

        devices = self.i2c.scan()

        print("Air I2C devices:", [
            hex(device) for device in devices
        ])

        if self.address not in devices:
            raise RuntimeError(
                "CCS811 not found at {}".format(
                    hex(self.address)
                )
            )

        hw_id = self.i2c.readfrom_mem(
            self.address,
            self.HW_ID,
            1
        )[0]

        print("CCS811 HW ID:", hex(hw_id))

        if hw_id != 0x81:
            raise RuntimeError(
                "Wrong CCS811 HW ID: {}".format(
                    hex(hw_id)
                )
            )

        status = self.i2c.readfrom_mem(
            self.address,
            self.STATUS,
            1
        )[0]

        if not (status & 0x10):
            raise RuntimeError(
                "CCS811 application firmware invalid"
            )

        # Start application mode
        self.i2c.writeto(
            self.address,
            bytes([self.APP_START])
        )

        time.sleep_ms(100)

        # Measurement every second
        self.i2c.writeto_mem(
            self.address,
            self.MEAS_MODE,
            bytes([0x10])
        )

        time.sleep_ms(100)

        print("CCS811 ready")

    def data_ready(self):
        status = self.i2c.readfrom_mem(
            self.address,
            self.STATUS,
            1
        )[0]

        return bool(status & 0x08)

    def read(self):
        if not self.data_ready():
            return None

        data = self.i2c.readfrom_mem(
            self.address,
            self.ALG_RESULT_DATA,
            4
        )

        eco2 = (data[0] << 8) | data[1]
        tvoc = (data[2] << 8) | data[3]

        return {
            "eco2": eco2,
            "tvoc": tvoc
        }