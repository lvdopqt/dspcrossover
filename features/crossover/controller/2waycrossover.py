
from features.crossover.service import CrossoverService
class NWayCrossover():

    def __init__(self, params, name='2way Crossover'):
        self.name = name
        self.params = self.parse_params(params)
        self.cursor_position = 0
        self.service = CrossoverService()

    def name(self):
        return self.name

    def next_cursor_position(self):
        self.cursor_position += 1
        if self.cursor_position > 3:
            self.cursor_position = 0

    def parse_params(self, params):
        """
        The 2-way crossover is composed of 4 filters, each with 5 coefficients, and a low invert filter.
        """
        return {
            'filter_1': params[0]['Parameter Address'],  # the head of a 5-coefficient filter
            'filter_2': params[5]['Parameter Address'],  # the head of another 5-coefficient filter
            'filter_3': params[10]['Parameter Address'],  # the head of another 5-coefficient filter
            'filter_4': params[15]['Parameter Address'],  # the head of another 5-coefficient filter
            'low_invert': params[20]['Parameter Address'] # NOTE: not used for now
        }

    def format_frequency(self, freq):
        """ Format the frequency to be displayed on the LCD """
        if freq >= 1000:
            return f"{freq/1000}kHz"
        return f"{freq}Hz"
    
    def format_frequency_cursor(self,freq, selected_freq):
        """ Format the frequency to be displayed on the LCD with cursor if selected """
        return f">{freq}" if freq == selected_freq else f"{freq}"

    def display(self):
        """ Display the current pair of channels on a 2-line LCD with cursor indication """
        ch_1_hpf, ch_1_lpf = self.service.extract_bandpass_cutoff_frequencies(self.params['filter_1'], self.params['filter_2'])
        ch_2_hpf, ch_2_lpf = self.service.extract_bandpass_cutoff_frequencies(self.params['filter_3'], self.params['filter_4'])
        
        # Map cursor positions to frequencies
        frequencies = [self.format_frequency(f) for f in [ch_1_hpf, ch_1_lpf, ch_2_hpf, ch_2_lpf]]
        selected_freq = frequencies[self.cursor_position]
            
        line1 = f"CH1: {self.format_frequency_cursor(ch_1_lpf, selected_freq)} - {self.format_frequency_cursor(ch_1_hpf, selected_freq)}"
        line2 = f"CH2: {self.format_frequency_cursor(ch_2_lpf, selected_freq)} - {self.format_frequency_cursor(ch_2_hpf, selected_freq)}"
        
        return f"{line1}\n{line2}"

    def set_frequency(self, low_cutoff, high_cutoff):
        """ Set the cutoff frequencies for a specific channel """
        self.service.set_bandpass_cutoff_frequencies(low_cutoff, high_cutoff)
    