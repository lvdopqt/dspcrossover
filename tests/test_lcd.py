# Visual test of LCD
# TODO: MAKE AND ACTUAL TEST

from machine import I2C, Pin
from lcd.i2c_lcd import I2cLcd
from time import sleep

i2c = I2C(scl=Pin(26), sda=Pin(27), freq=400000)

lcd = I2cLcd(i2c, 0x27, 2, 16)

caixa_alta_string = 'CAIXA ALTA \n SOUNDSYSTEM'
while True:
    lcd.clear()
    for i in range(24):
        lcd.putstr(caixa_alta_string[i])
        sleep(0.5)