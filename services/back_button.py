from machine import Pin
import time

class BackButton:
    def __init__(self, back_pin, event_bus):
        # Configura o botão "back"
        self.back_button = Pin(back_pin, Pin.IN, Pin.PULL_UP)

        # EventBus para emitir eventos
        self.event_bus = event_bus

        # Configura interrupção para o botão de "back"
        self.back_button.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_back)

    def handle_back(self, pin):
        """Emite o evento de 'back' quando o botão é pressionado."""
        # Debounce simples
        time.sleep_ms(50)
        if self.back_button.value() == 0:  # Confirma que o botão ainda está pressionado
            self.event_bus.emit("back")
