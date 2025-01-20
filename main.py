from machine import I2C, Pin
import time

from external.sigma.sigma_dsp.adau.adau1401.adau1401 import ADAU1401 as ADAU
from external.sigma.bus.adapters import I2C as SigmaI2C
from external.lcd.i2c_lcd import I2cLcd

from config import (
    DSP_SCL_PIN, DSP_SCA_PIN,
    ROTARY_ENCODER_CLK_PIN, ROTARY_ENCODER_DT_PIN, ROTARY_ENCODER_SW_PIN,
    BACK_BUTTON_PIN, LCD_SCL_PIN, LCD_SDA_PIN, I2C_FREQ
)

from features.events.event_bus import EventBus
from features.navigator.controller import Navigator
from features.rotary_encoder import RotaryEncoder
from features.back_button import BackButton
from features.crossover.controller import TwoWayCrossover
from utils.get_params import get_params

class App:
    def __init__(self):
        """Initialize the application."""
        self.event_bus = self._initialize_event_bus()
        self.dsp = self._initialize_dsp()
        self.lcd = self._initialize_lcd()
        self.params = self._load_params()
        self.encoder = self._initialize_rotary_encoder()
        self.back_button = self._initialize_back_button()
        self.two_way_crossover = self._initialize_crossover()
        self.navigator = self._initialize_navigator()
        self._register_event_listeners()

    def _initialize_event_bus(self):
        """Initialize and return the EventBus."""
        return EventBus()

    def _initialize_dsp(self):
        """Initialize and return the DSP."""
        dsp_i2c = I2C(scl=Pin(DSP_SCL_PIN), sda=Pin(DSP_SCA_PIN), freq=I2C_FREQ)
        bus = SigmaI2C(dsp_i2c)
        return ADAU(bus)

    def _initialize_lcd(self):
        """Initialize and return the LCD."""
        lcd_i2c = I2C(scl=Pin(LCD_SCL_PIN), sda=Pin(LCD_SDA_PIN), freq=I2C_FREQ)
        return I2cLcd(lcd_i2c, 0x27, 2, 16)

    def _load_params(self):
        """Load and return the parameters."""
        return get_params()

    def _initialize_rotary_encoder(self):
        """Initialize and return the RotaryEncoder."""
        return RotaryEncoder(
            clk_pin=Pin(ROTARY_ENCODER_CLK_PIN),
            dt_pin=Pin(ROTARY_ENCODER_DT_PIN),
            sw_pin=Pin(ROTARY_ENCODER_SW_PIN),
            event_bus=self.event_bus
        )

    def _initialize_back_button(self):
        """Initialize and return the BackButton."""
        return BackButton(back_button_pin=Pin(BACK_BUTTON_PIN, Pin.IN, Pin.PULL_UP), event_bus=self.event_bus)

    def _initialize_crossover(self):
        """Initialize and return the TwoWayCrossover."""
        return TwoWayCrossover(self.dsp, self.params['Crossover1'])

    def _initialize_navigator(self):
        """Initialize and return the Navigator."""
        return Navigator(
            event_bus=self.event_bus,
            lcd=self.lcd,
            current_page=self.two_way_crossover
        )

    def _register_event_listeners(self):
        """Register event listeners on the EventBus."""
        self.event_bus.subscribe("right", self.navigator.on_right)
        self.event_bus.subscribe("left", self.navigator.on_left)
        self.event_bus.subscribe("click", self.navigator.on_click)
        self.event_bus.subscribe("back", self.navigator.on_back)

    def run(self):
        """Main loop to continuously read the encoder state."""
        while True:
            self.encoder.read()  # Checks for encoder rotation
            time.sleep(0.01)  # Small delay to reduce CPU usage

# Create and run the app
if __name__ == "__main__":
    app = App()
    app.run()