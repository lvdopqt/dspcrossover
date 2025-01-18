# Import the RotaryEncoder class
from features.rotary_encoder.rotary_encoder import RotaryEncoder

# Mock machine module
class MockMachine:
    class Pin:
        IN = 1
        PULL_UP = 2
        IRQ_FALLING = 4

        def __init__(self, pin, mode, pull):
            self._value = 1  # Default to not pressed (pull-up)
            self._handler = None

        def value(self):
            print(f"Reading pin value: {self._value}")
            return self._value

        def irq(self, trigger, handler):
            print("Setting up IRQ handler...")
            self._handler = handler

        def simulate_press(self):
            print("Simulating button press...")
            self._value = 0  # Button pressed
            if self._handler:
                print("Calling IRQ handler...")
                self._handler(self)

        def simulate_release(self):
            print("Simulating button release...")
            self._value = 1  # Button released

# Replace the real machine module with the mock one
import sys
sys.modules["machine"] = MockMachine()

# Mock event bus
class MockEventBus:
    def __init__(self):
        self.events = []

    def emit(self, event):
        print(f"Emitting event: {event}")
        self.events.append(event)

# Test function
def test_rotary_encoder():
    event_bus = MockEventBus()
    mock_clk = MockMachine.Pin(12, MockMachine.Pin.IN, MockMachine.Pin.PULL_UP)
    mock_dt = MockMachine.Pin(13, MockMachine.Pin.IN, MockMachine.Pin.PULL_UP)
    mock_sw = MockMachine.Pin(14, MockMachine.Pin.IN, MockMachine.Pin.PULL_UP)

    # Create RotaryEncoder instance with the mock pins, event bus, and trigger value
    encoder = RotaryEncoder(
        clk_pin=mock_clk,
        dt_pin=mock_dt,
        sw_pin=mock_sw,
        event_bus=event_bus,
        irq_trigger=MockMachine.Pin.IRQ_FALLING
    )

    # Simulate a click event
    mock_sw.simulate_press()

    # Verify if the "click" event was emitted
    assert "click" in event_bus.events, "Click event was not emitted"

    # Simulate a right rotation
    mock_clk._value = 0
    mock_dt._value = 0
    encoder.read()

    # Verify if the "right" event was emitted
    assert "right" in event_bus.events, "Right event was not emitted"

    # Simulate a left rotation
    mock_clk._value = 1
    mock_dt._value = 0
    encoder.read()

    # Verify if the "left" event was emitted
    assert "left" in event_bus.events, "Left event was not emitted"