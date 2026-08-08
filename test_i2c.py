from machine import Pin, I2C

lcd_bus = I2C(
    0,
    sda=Pin(4),
    scl=Pin(5),
    freq=100000
)

air_bus = I2C(
    1,
    sda=Pin(26),
    scl=Pin(27),
    freq=100000
)

print("LCD BUS:")
for address in lcd_bus.scan():
    print(hex(address))

print("AIR BUS:")
for address in air_bus.scan():
    print(hex(address))