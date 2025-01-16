from machine import I2C, Pin
from external.lcd.i2c_lcd import I2cLcd
from features.crossover.controller import TwoWayCrossover

class Navigator:
    def __init__(self, dsp, params, event_bus):
        # Init I2c LCD
        i2c = I2C(scl=Pin(26), sda=Pin(27), freq=400000)
        self.lcd = I2cLcd(i2c, 0x27, 2, 16)

        self.current_page_index = 0
        self.current_page = TwoWayCrossover(dsp, params)
        
        event_bus.subscribe("click", self.on_click)
        event_bus.subscribe("back", self.on_back)
        self.display_current_page()

    def display_current_page(self):
        self.lcd.clear()
        display_text = self.current_page.display()
        self.lcd.putstr(display_text)
    
    def on_click(self, data=None):
        self.current_page.on_click()

    def on_back(self, data=None):
        self.current_page.on_back()
    
    def on_right(self, data=None):
        self.current_page.on_right()

    def on_left(self, data=None):
        self.current_page.on_left()