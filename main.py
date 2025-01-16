import json
from machine import I2C, Pin

from external.sigma.sigma_dsp.adau.adau1401.adau1401 import ADAU1401 as ADAU
from external.sigma.bus.adapters import I2C as SigmaI2C

from config import DSP_SCL_PIN, DSP_SCA_PIN, ROTARY_ENCODER_CLK_PIN,ROTARY_ENCODER_DT_PIN, ROTARY_ENCODER_SW_PIN, BACK_BUTTON_PIN

from features.events.event_bus import EventBus
from features.navigator.controller import Navigator
from features.rotary_encoder import RotaryEncoder
from features.back_button import BackButton



# Initialize the EventBus
event_bus = EventBus()

# Initialize DSP and addresses
i2c = I2C(scl=Pin(DSP_SCL_PIN), sda=Pin(DSP_SCA_PIN), freq=400000)
bus = SigmaI2C(i2c)
dsp = ADAU(bus)

params = None  # Replace with required params

# Initialize the Navigator and register it with the EventBus
navigator = Navigator(dsp, addresses, event_bus)

# Initialize RotaryEncoder and BackButton with the EventBus
encoder = RotaryEncoder(
        clk_pin=ROTARY_ENCODER_CLK_PIN,
        dt_pin=ROTARY_ENCODER_DT_PIN,
        sw_pin=ROTARY_ENCODER_SW_PIN,
        event_bus=event_bus
    )  
back_button = BackButton(back_pin=BACK_BUTTON_PIN, event_bus=event_bus)  # Back button pin

# Register event listeners on EventBus to handle navigation actions
event_bus.subscribe("right", navigator.next_page)
event_bus.subscribe("left", navigator.previous_page)
event_bus.subscribe("click", navigator.on_click)
event_bus.subscribe("back", navigator.on_back)

# Main loop to continuously read the encoder state
while True:
    encoder.read()  # Checks for encoder rotation
    # Small delay to reduce CPU usage
    time.sleep(0.01)
