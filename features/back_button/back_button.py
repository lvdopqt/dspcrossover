from machine import Pin
import time

class BackButton:
    def __init__(self, back_pin, event_bus):
        # Configures the back button
        self.back_button = Pin(back_pin, Pin.IN, Pin.PULL_UP)

        self.event_bus = event_bus

        # Triggers self.handle_back if configured 
        self.back_button.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_back)

    def handle_back(self, pin):
        # Debounce avoid double clicking
        time.sleep_ms(50)
        if self.back_button.value() == 0:  # Confirms the button still down
            self.event_bus.emit("back")
