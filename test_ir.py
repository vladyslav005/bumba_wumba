from services.ir_service import IRService
import time


ir = IRService(pin=15)

print("IR ready")
print("Press remote buttons...")


while True:
    result = ir.read()

    if result is not None:
        print(
            "Address:",
            hex(result["address"]),
            "Command:",
            hex(result["command"])
        )

    time.sleep_ms(20)