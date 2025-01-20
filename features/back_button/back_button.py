import time

class BackButton:
    def __init__(self, back_button_pin, event_bus):
        """
        Initialize the BackButton.

        Args:
            back_button_pin (Pin): A configured Pin instance for the back button.
            event_bus: The event bus to emit events to.
        """
        self.back_button = back_button_pin
        self.event_bus = event_bus

        # Set up the IRQ handler
        self.back_button.irq(trigger=self.back_button.IRQ_FALLING, handler=self.handle_back)

        # Variables for debouncing
        self.last_click_time = 0  # Track the last click time
        self.debounce_time = 10

    def handle_back(self, pin):
        """
        Handle the button press event.
        """
        current_time = time.ticks_ms()
        if current_time - self.last_click_time > self.debounce_time:  # Debounce check
            self.last_click_time = current_time
            self.event_bus.emit("back")