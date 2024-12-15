class BaseController:
    def __init__(self, dsp, addresses):
        self.addresses = addresses
        self.dsp = dsp

    def display(self):
        """ Display the current state of the controller """
        pass

    def next_page(self):
        """ Navigate to the next page (next pair of channels) """
        self.current_page = (self.current_page + 1) % (self.n // 2)
        self.cursor_position = 0  # Reset cursor to the top of the page
        self.display()
    
    def previous_page(self):
        """ Navigate to the previous page (previous pair of channels) """
        self.current_page = (self.current_page - 1) % (self.n // 2)
        self.cursor_position = 0  # Reset cursor to the top of the page
        self.display()

    def move_cursor_up(self):
        """ Move the cursor up within the current page """
        if self.cursor_position > 0:
            self.cursor_position -= 1
        else:
            self.cursor_position = 1  # Wrap around to the last position if at the top
        self.display()

    def move_cursor_down(self):
        """ Move the cursor down within the current page """
        if self.cursor_position < 1:
            self.cursor_position += 1
        else:
            self.cursor_position = 0  # Wrap around to the first position if at the bottom
        self.display()