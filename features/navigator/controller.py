from features.crossover.controller import TwoWayCrossover

class Navigator:
    def __init__(self, event_bus, lcd, current_page):
        self.lcd = lcd

        self.current_page_index = 0
        self.current_page = current_page
        
        event_bus.subscribe("click", self.on_click)
        event_bus.subscribe("back", self.on_back)
        self.display_current_page()

    def display_current_page(self):
        self.lcd.clear()
        display_text = self.current_page.display()
        self.lcd.putstr(display_text)
    
    def on_click(self, data=None):
        self.current_page.on_click()
        self.display_current_page()

    def on_back(self, data=None):
        self.current_page.on_back()
        self.display_current_page()
    
    def on_right(self, data=None):
        self.current_page.on_right()
        self.display_current_page()

    def on_left(self, data=None):
        self.current_page.on_left()
        self.display_current_page()