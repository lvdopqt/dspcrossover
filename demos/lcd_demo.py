# Visual test of LCD

from machine import I2C, Pin
from time import sleep

from config import LCD_SCL_PIN, LCD_SDA_PIN, I2C_FREQ
from external.lcd.i2c_lcd import I2cLcd

i2c = I2C(scl=Pin(LCD_SCL_PIN), sda=Pin(LCD_SDA_PIN), freq=I2C_FREQ)

lcd = I2cLcd(i2c, 0x27, 2, 16)

caixa_alta_string = 'CAIXA ALTA \n SOUNDSYSTEM'
while True:
    lcd.clear()
    for i in range(24):
        lcd.putstr(caixa_alta_string[i])
        sleep(0.5)