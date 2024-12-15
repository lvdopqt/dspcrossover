from machine import Pin
from rotary_encoder import RotaryEncoder
import time

# Mock event bus
class MockEventBus:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)

# Mock Pin class
class MockPin:
    def __init__(self, pin, mode, pull):
        self._value = 1  # Default to not pressed or inactive state
        self._handler = None

    def value(self):
        return self._value

    def irq(self, trigger, handler):
        self._handler = handler

    def simulate_press(self):
        self._value = 0  # Button pressed (falling edge)
        if self._handler:
            self._handler(self)
        self._value = 1  # Reset to released state

    def simulate_change(self, value):
        self._value = value

# Test function
def test_rotary_encoder():
    # Initialize mock event bus and mock pins for CLK, DT, and SW
    event_bus = MockEventBus()
    clk_pin = MockPin(1, Pin.IN, Pin.PULL_UP)
    dt_pin = MockPin(2, Pin.IN, Pin.PULL_UP)
    sw_pin = MockPin(3, Pin.IN, Pin.PULL_UP)

    # Create RotaryEncoder instance
    encoder = RotaryEncoder(clk_pin=clk_pin, dt_pin=dt_pin, sw_pin=sw_pin, event_bus=event_bus)

    # Simulate button click
    sw_pin.simulate_press()

    # Simulate rotation to the right
    clk_pin.simulate_change(0)
    dt_pin.simulate_change(0)
    encoder.read()
    
    clk_pin.simulate_change(1)
    dt_pin.simulate_change(1)
    encoder.read()

    # Simulate rotation to the left
    clk_pin.simulate_change(0)
    dt_pin.simulate_change(1)
    encoder.read()
    
    clk_pin.simulate_change(1)
    dt_pin.simulate_change(0)
    encoder.read()

    # Print the events emitted
    print("Events emitted:", event_bus.events)  # Expected output: ['click', 'right', 'left']

# Run the test
test_rotary_encoder()
