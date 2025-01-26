class Navigator:
    def __init__(self, lcd, initial_page):
        self.lcd = lcd
        self.page_stack = [initial_page]
        self.display_current_page()

    @property
    def current_page(self):
        return self.page_stack[-1]

    def display_current_page(self):
        self.lcd.clear()
        display_text = self.current_page.display()
        self.lcd.putstr(display_text)

    def navigate_to(self, page):
        self.page_stack.append(page)
        self.display_current_page()

    def go_back(self):
        if len(self.page_stack) > 1:
            self.page_stack.pop()
            self.display_current_page()

    def on_click(self, data=None):
        self.current_page.on_click(navigator=self)
        self.display_current_page()

    def on_back(self, data=None):
        handled = self.current_page.on_back()
        if handled:
            self.display_current_page()
        else:
            self.go_back()

    def on_right(self, data=None):
        self.current_page.on_right()
        self.display_current_page()

    def on_left(self, data=None):
        self.current_page.on_left()
        self.display_current_page()