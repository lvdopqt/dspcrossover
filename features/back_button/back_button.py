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

    def handle_back(self, pin):
        """
        Handle the button press event.
        """
        # Debounce to avoid double-clicking
        time.sleep_ms(50)
        if self.back_button.value() == 1:  # Confirm the button is still pressed
            self.event_bus.emit("back")