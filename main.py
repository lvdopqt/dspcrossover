from features.events.event_bus import EventBus
from features.navigator.controller import Navigator
from features.rotary_encoder import RotaryEncoder
from features.back_button import BackButton

# Initialize the EventBus
event_bus = EventBus()

# Initialize DSP and addresses (replace with actual instances)
dsp = None  # Replace with real DSP instance
addresses = None  # Replace with required addresses

# Initialize the Navigator and register it with the EventBus
navigator = Navigator(dsp, addresses, event_bus)

# Initialize RotaryEncoder and BackButton with the EventBus
encoder = RotaryEncoder(clk_pin=32, dt_pin=33, sw_pin=25, event_bus=event_bus)  # Encoder pins
back_button = BackButton(back_pin=26, event_bus=event_bus)  # Back button pin

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
