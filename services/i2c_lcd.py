"""Implements a HD44780 character LCD connected via PCF8574 on I2C."""

import time
from machine import I2C

from services.lcd_api import LcdApi

# The PCF8574 has a jumper selectable address: 0x20 - 0x27
DEFAULT_I2C_ADDR = 0x27

# Defines shifts or masks for the various LCD line attached to the PCF8574
MASK_RS = 0x01
MASK_RW = 0x02
MASK_E = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4


class I2cLcd(LcdApi):
    """Implements a HD44780 character LCD connected via PCF8574 on I2C."""

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.i2c.writeto(self.i2c_addr, bytes([0x00]))  # Inicializa o PCF8574
        time.sleep(0.020)  # Aguarda o tempo de inicialização do LCD
        # Envia o reset 3 vezes
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.005)  # Precisa de um atraso de pelo menos 4,1 ms
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)
        # Coloca o LCD em modo de 4 bits
        self.hal_write_init_nibble(self.LCD_FUNCTION)
        time.sleep(0.001)
        LcdApi.__init__(self, num_lines, num_columns)
        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)

    def hal_write_init_nibble(self, nibble):
        """Escreve um nibble de inicialização no LCD.

        Essa função é usada apenas durante a inicialização.
        """
        byte = ((nibble >> 4) & 0x0f) << SHIFT_DATA
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))

    def hal_backlight_on(self):
        """Liga o backlight."""
        self.i2c.writeto(self.i2c_addr, bytes([1 << SHIFT_BACKLIGHT]))

    def hal_backlight_off(self):
        """Desliga o backlight."""
        self.i2c.writeto(self.i2c_addr, bytes([0]))

    def hal_sleep_us(self, usecs):
        """Aguarda por um tempo em microsegundos."""
        time.sleep(usecs / 1000000)

    def hal_write_command(self, cmd):
        """Escreve um comando no LCD."""
        byte = ((self.backlight << SHIFT_BACKLIGHT) |
                (((cmd >> 4) & 0x0f) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = ((self.backlight << SHIFT_BACKLIGHT) |
                ((cmd & 0x0f) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        if cmd <= 3:
            time.sleep(0.005)  # Delay necessário para comandos 'home' e 'clear'

    def hal_write_data(self, data):
        """Escreve dados no LCD."""
        byte = (MASK_RS |
                (self.backlight << SHIFT_BACKLIGHT) |
                (((data >> 4) & 0x0f) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = (MASK_RS |
                (self.backlight << SHIFT_BACKLIGHT) |
                ((data & 0x0f) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
