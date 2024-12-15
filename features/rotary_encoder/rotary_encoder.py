from machine import Pin

class RotaryEncoder:
    def __init__(self, clk_pin, dt_pin, sw_pin, event_bus):
        # Configures PINS for CLK, DT and switch/click button (SW)
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
        
        # Monitors state changes
        self.last_clk = self.clk.value()
        
        self.event_bus = event_bus

        # Triggers self.handle_click if switch button is clicked
        self.sw.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_click)

    def handle_click(self, pin):
        """Emits a click event if the switch is clicked"""
        self.event_bus.emit("click")

    def read(self):
        """Verify the direction of encoder rotation and emits right and left events"""
        current_clk = self.clk.value()
        current_dt = self.dt.value()
        
        if current_clk != self.last_clk:  # Detects change in the clock
            # If DT value is equal to clock its moving right
            if current_dt == current_clk:
                self.event_bus.emit("right")
            else:
                self.event_bus.emit("left")
        
        # Updates last clock value
        self.last_clk = current_clk