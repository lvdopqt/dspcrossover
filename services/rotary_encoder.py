from machine import Pin

class RotaryEncoder:
    def __init__(self, clk_pin, dt_pin, sw_pin, event_bus):
        # Configura pinos para o CLK, DT e botão de click (SW)
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
        
        # Para rastrear mudanças de estado
        self.last_clk = self.clk.value()
        
        # EventBus para emitir eventos
        self.event_bus = event_bus

        # Configura uma interrupção para detectar o clique no botão
        self.sw.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_click)

    def handle_click(self, pin):
        """Emite o evento de click quando o botão é pressionado."""
        self.event_bus.emit("click")

    def read(self):
        """Verifica a direção da rotação e emite eventos de 'left' e 'right'."""
        current_clk = self.clk.value()
        current_dt = self.dt.value()
        
        if current_clk != self.last_clk:  # Detecta mudança no pino CLK
            # Se o valor de DT é igual ao de CLK, o giro é para a direita
            if current_dt == current_clk:
                self.event_bus.emit("right")
            else:
                self.event_bus.emit("left")
        
        # Atualiza o último valor de CLK
        self.last_clk = current_clk