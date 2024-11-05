
from controllers.base import BaseController
from services.crossover import Crossover as CrossoverService

class Crossover(BaseController):
    def __init__(self, dsp, address):
        self.address = address
        self.service = CrossoverService(dsp)

    def format_bandpass_display(self, low_cut, high_cut):
        """Format frequencies for a 2-line display."""
        return f'Low Cut: {low_cut} Hz\nHigh Cut: {high_cut} Hz'
    
    def display(self):
        """Retrieve and format current bandpass settings for display."""
        try:
            low_cut, high_cut = self.service.get_bandpass_cutoff_frequencies(self.address)
            return self.format_bandpass_display(low_cut, high_cut)
        except Exception as e:
            return f"Error: {str(e)}"

    def set_bandpass_cutoff_frequencies(self, low_cut, high_cut):
        """Set new bandpass cutoff frequencies in the DSP."""
        try:
            self.service.set_bandpass_cutoff_frequencies(low_cut, high_cut, self.address)
        except ValueError as ve:
            print(f"Invalid frequency values: {ve}")
        except Exception as e:
            print(f"Error communicating with DSP: {e}")
    
    def get_bandpass_cutoff_frequencies(self):
        """Direct access to get current frequencies for other uses if needed."""
        return self.service.get_bandpass_cutoff_frequencies(self.address)
