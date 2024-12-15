import gc
from features.controllers.base import BaseController
from features.crossover.controller.crossover import Crossover

class NWayCrossover(BaseController):
    default_n = 4
    channels_names = ["Low", "Low-Mid", "High-Mid", "High"]

    def __init__(self, addresses, name='3way Crossover'):
        super().__init__()
        self.name = name
        self.n = self.default_n
        self.addresses = addresses
        self.channels_names = self.channels_names
        self.current_page = 0  # Tracks which pair of channels to display
        self.cursor_position = 0  # Tracks cursor position within the displayed channels
        self.crossover_cache = {}  # Cache to hold initialized Crossover instances

    @classmethod
    def name(cls):
        return f'{cls.default_n}-Way Crossover'
    
    def display(self):
        """ Display the current pair of channels on a 2-line LCD with cursor indication """
        start_channel = self.current_page * 2
        end_channel = start_channel + 2
        
        display_text = ""
        for i in range(start_channel, end_channel):
            channel_number = i + 1
            channel_name = self.channels_names[i]
            low_cutoff, high_cutoff = self.get_frequency(channel_number)
            
            # Indicate the cursor position
            cursor = ">" if i - start_channel == self.cursor_position else " "
            display_text += f"{cursor} CH{channel_number}: {channel_name}\n{low_cutoff}Hz - {high_cutoff}Hz\n"

        # Only display two lines for the LCD
        lines = display_text.splitlines()
        return '\n'.join(lines[:2])

    def display_channels(self):
        """ Return the full layout as a string (for debugging or other uses) """
        return (
            f'CH1: {self.channels_names[0]}\n'
            f'CH2: {self.channels_names[1]}\n'
            f'CH3: {self.channels_names[2]}\n'
            f'CH4: {self.channels_names[3]}'
        )

    
    def _get_or_create_crossover(self, channel):
        """ Lazy-load or create a Crossover instance for the specified channel. Clears other instances from cache. """
        
        # If the requested channel is already cached, just return it
        if channel in self.crossover_cache:
            return self.crossover_cache[channel]
        
        # Remove references to other channels, freeing memory
        for key in list(self.crossover_cache.keys()):
            del self.crossover_cache[key]
        
        # Explicitly call garbage collection to free memory
        gc.collect()
        
        # Create and cache the new Crossover instance for the specified channel
        channel_address = self.addresses[channel]  # Calculate address based on channel
        self.crossover_cache[channel] = Crossover(self.dsp, channel_address)
        
        return self.crossover_cache[channel]

    def set_frequency(self, channel, low_cutoff, high_cutoff):
        """ Set the cutoff frequencies for a specific channel """
        if channel < 1 or channel > self.n:
            raise ValueError("Invalid channel number")
        crossover = self._get_or_create_crossover(channel)
        crossover.set_bandpass_cutoff_frequencies(low_cutoff, high_cutoff)
    
    def get_frequency(self, channel):
        """ Get the cutoff frequencies for a specific channel """
        if channel < 1 or channel > self.n:
            raise ValueError("Invalid channel number")
        crossover = self._get_or_create_crossover(channel)
        return crossover.get_bandpass_cutoff_frequencies()
