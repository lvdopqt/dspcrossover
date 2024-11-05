from machine import I2C, Pin
from services.i2c_lcd import I2cLcd
from time import sleep

# Inicializa o I2C
i2c = I2C(scl=Pin(26), sda=Pin(27), freq=400000)

# Inicializa o LCD
lcd = I2cLcd(i2c, 0x27, 2, 16)  # Ajuste o endereço e tamanho conforme necessário

# Teste de escrita no LCD
caixa_alta_string = 'CAIXA ALTA \n SOUNDSYSTEM'
while True:
    lcd.clear()
    for i in range(24):
        lcd.putstr(caixa_alta_string[i])
        sleep(0.5)