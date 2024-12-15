from features.menu import Menu
from lcd.i2c_lcd import I2cLcd
from machine import I2C, Pin

class Navigator:
    def __init__(self, dsp, addresses, event_bus):
        # Inicializa o I2C e o LCD
        i2c = I2C(scl=Pin(26), sda=Pin(27), freq=400000)
        self.lcd = I2cLcd(i2c, 0x27, 2, 16)

        
        # Controle de navegação
        self.current_page_index = 0
        self.current_page = Menu(dsp, addresses)
        
        # Registra o Navigator nos eventos do bus
        event_bus.subscribe("click", self.on_click)
        event_bus.subscribe("back", self.on_back)
        self.display_current_page()

    def display_current_page(self):
        """Exibe o conteúdo da página atual no LCD"""
        self.lcd.clear()
        display_text = self.current_page.display()  # Chama o método `display` da página atual
        self.lcd.putstr(display_text)
    
    def on_click(self, data=None):
        """Responde ao evento de click"""
        action = self.current_page.click()  # Executa o método `click` da página atual
        self.display_current_page()
        return action

    def on_back(self, data=None):
        """Responde ao evento de voltar para a página anterior"""
        self.previous_page()
    
    def next_page(self):
        """Navega para a próxima página"""
        self.current_page_index = (self.current_page_index + 1) % len(self.pages)
        self.current_page = self.pages[self.current_page_index]
        self.display_current_page()
    
    def previous_page(self):
        """Navega para a página anterior"""
        self.current_page_index = (self.current_page_index - 1) % len(self.pages)
        self.current_page = self.pages[self.current_page_index]
        self.display_current_page()