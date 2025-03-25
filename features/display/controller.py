class Display:
    
    def __init__(self, lcd=None, oled=None, device='lcd'):
        self.lcd = lcd
        self.oled = oled
        self.device = device

    def show_lcd(self, content):
        self.lcd.clear()
        self.lcd.putstr(display_text)

    def show_oled(self, content):
        self.oled.fill(0)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            self.oled.text(line, 0, i * 10)
        self.oled.show()


    def show(self, content):
        if self.device == 'oled':
            self.show_oled(content)
        else:
            self.show_lcd(content)
