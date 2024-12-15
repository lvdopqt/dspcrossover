from features.back_button import BackButton
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
        self._value = 1  # Default to not pressed (pull-up)
        self._handler = None

    def value(self):
        return self._value

    def irq(self, trigger, handler):
        self._handler = handler

    def simulate_press(self):
        self._value = 0  # Button pressed
        if self._handler:
            self._handler(self)

    def simulate_release(self):
        self._value = 1  # Button released

# Test function
def test_back_button():
    event_bus = MockEventBus()
    mock_pin = MockPin(12, Pin.IN, Pin.PULL_UP)

    # Create BackButton instance with the mock pin and event bus
    back_button = BackButton(back_pin=mock_pin, event_bus=event_bus)

    # Simulate button press
    mock_pin.simulate_press()

    # Verify if the "back" event was emitted
    print("Events emitted:", event_bus.events)  # Expected output: ['back']

# Run the test
test_back_button()
