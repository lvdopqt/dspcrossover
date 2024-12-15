
from features.controllers.base import BaseController
from features.compressor.controller import Compressor
from features.crossover.controller.nwaycrossover import NWayCrossover
from features.mixer.controller import InputMixer


class Menu(BaseController):
    def __init__(self):
        super().__init__()
        self.menu = [
            InputMixer,
            NWayCrossover,
            Compressor,
        ]
        self.current_page = 0
        self.cursor_position = 0
        self.menu_cache = {}

    def display(self):
        start_index = self.current_page * 2
        end_index = start_index + 2

        display_text = ""
        for i, item in enumerate(self.menu):
            if start_index <= i < end_index:
                cursor = ">" if i == self.cursor_position else " "
                display_text += f"`{cursor} {item.name()}`\n"

        lines = display_text.splitlines()
        return '\n'.join(lines[:2])
    
    def click(self):
        item = self.menu[self.cursor_position]

        if item not in self.menu_cache:
            for key in list(self.menu_cache.keys()):
                del self.menu_cache[key]
            self.menu_cache[item] = item(self.dsp, self.addresses)
        return self.menu_cache[item]