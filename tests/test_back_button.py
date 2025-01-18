from features.back_button.back_button import BackButton

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
            print(f"Reading button value: {self._value}")
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

# Mock time module (for time.sleep_ms)
class MockTime:
    def sleep_ms(self, delay):
        print(f"Sleeping for {delay} ms...")
        pass  # Do nothing for testing

sys.modules["time"] = MockTime()

# Mock event bus
class MockEventBus:
    def __init__(self):
        self.events = []

    def emit(self, event):
        print(f"Emitting event: {event}")
        self.events.append(event)

# Test function
def test_back_button():
    event_bus = MockEventBus()
    mock_pin = MockMachine.Pin(12, MockMachine.Pin.IN, MockMachine.Pin.PULL_UP)

    # Create BackButton instance with the mock pin and event bus
    back_button = BackButton(back_button_pin=mock_pin, event_bus=event_bus)

    # Simulate button press
    mock_pin.simulate_press()

    # Verify if the "back" event was emitted
    assert "back" in event_bus.events, "Back event was not emitted"
