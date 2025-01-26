class Menu:
    CURSOR_SYMBOL = '>'
    
    def __init__(self, items, name='Menu'):
        self.name = name
        self.items = items
        self.cursor_position = 0
        self.max_cursor_position = len(items) - 1

    def display(self):
        line1 = f"{self.CURSOR_SYMBOL if self.cursor_position == 0 else ' '} {self.items[0].name}"
        line2 = f"{self.CURSOR_SYMBOL if self.cursor_position == 1 else ' '} {self.items[1].name}"
        return f"{line1}\n{line2}"

    def on_click(self, navigator=None):
        if navigator:
            selected_item = self.items[self.cursor_position]
            navigator.navigate_to(selected_item)

    def on_back(self):
        # As the root page, back does nothing
        return True  # Prevent exiting the menu

    def on_right(self):
        self.cursor_position = min(self.cursor_position + 1, self.max_cursor_position)

    def on_left(self):
        self.cursor_position = max(self.cursor_position - 1, 0)