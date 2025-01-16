from features.crossover.service import CrossoverService

class TwoWayCrossover():
    MAX_CURSOR_POSITION = 3

    def __init__(self, dsp, params, name='2way Crossover'):
        self.name = name
        self.params = self.parse_params(params)
        self.cursor_position = 0
        self.service = CrossoverService(dsp)
        self.selected_filter = None  # Track which filter is selected for adjustment
        self.temp_frequencies = {}   # Store temporary frequency adjustments

    def name(self):
        return self.name

    def update_cursor_position(self, direction):
        if direction == "right":
            self.cursor_position += 1
        elif direction == "left":
            self.cursor_position -= 1
        
        # Wrap around if the cursor position goes out of bounds
        if self.cursor_position > self.MAX_CURSOR_POSITION:
            self.cursor_position = 0
        elif self.cursor_position < 0:
            self.cursor_position = self.MAX_CURSOR_POSITION

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
            return f"{freq/1000:.1f}kHz"
        return f"{freq}Hz"
    
    def format_frequency_cursor(self, freq, selected_freq):
        """ Format the frequency to be displayed on the LCD with cursor if selected """
        return f">{freq}" if freq == selected_freq else f"{freq}"

    def display(self):
        """ Display the current pair of channels on a 2-line LCD with cursor indication """
        ch_1_hpf, ch_1_lpf = self.service.extract_bandpass_cutoff_frequencies(self.params['filter_1'], self.params['filter_2'])
        ch_2_hpf, ch_2_lpf = self.service.extract_bandpass_cutoff_frequencies(self.params['filter_3'], self.params['filter_4'])
        
        # Use temporary frequencies if a filter is selected
        if self.selected_filter is not None:
            ch_1_hpf = self.temp_frequencies.get('ch_1_hpf', ch_1_hpf)
            ch_1_lpf = self.temp_frequencies.get('ch_1_lpf', ch_1_lpf)
            ch_2_hpf = self.temp_frequencies.get('ch_2_hpf', ch_2_hpf)
            ch_2_lpf = self.temp_frequencies.get('ch_2_lpf', ch_2_lpf)
        
        # Map cursor positions to frequencies
        frequencies = [self.format_frequency(f) for f in [ch_1_hpf, ch_1_lpf, ch_2_hpf, ch_2_lpf]]
        selected_freq = frequencies[self.cursor_position]
            
        line1 = f"CH1: {self.format_frequency_cursor(ch_1_lpf, selected_freq)} - {self.format_frequency_cursor(ch_1_hpf, selected_freq)}"
        line2 = f"CH2: {self.format_frequency_cursor(ch_2_lpf, selected_freq)} - {self.format_frequency_cursor(ch_2_hpf, selected_freq)}"
        
        return f"{line1}\n{line2}"

    def set_frequency(self, low_cutoff, high_cutoff, head_address):
        """ Set the cutoff frequencies for a specific channel """
        self.service.set_bandpass_cutoff_frequencies(low_cutoff, high_cutoff, head_address)

    def on_click(self, data=None):
        """ Handle click events """
        if self.selected_filter is None:
            # Select the filter for adjustment
            self.selected_filter = self.cursor_position
            # Initialize temporary frequencies
            ch_1_hpf, ch_1_lpf = self.service.extract_bandpass_cutoff_frequencies(self.params['filter_1'], self.params['filter_2'])
            ch_2_hpf, ch_2_lpf = self.service.extract_bandpass_cutoff_frequencies(self.params['filter_3'], self.params['filter_4'])
            self.temp_frequencies = {
                'ch_1_hpf': ch_1_hpf,
                'ch_1_lpf': ch_1_lpf,
                'ch_2_hpf': ch_2_hpf,
                'ch_2_lpf': ch_2_lpf
            }
        else:
            # Map selected filter to the corresponding frequency keys
            filter_to_frequencies = {
                0: ('ch_1_lpf', 'ch_1_hpf'),
                1: ('ch_1_lpf', 'ch_1_hpf'),
                2: ('ch_2_lpf', 'ch_2_hpf'),
                3: ('ch_2_lpf', 'ch_2_hpf')
            }
            low_key, high_key = filter_to_frequencies[self.selected_filter]
            self.set_frequency(
                self.temp_frequencies[low_key],
                self.temp_frequencies[high_key],
                self.params[self.selected_filter]
            )
            
            # Reset selection
            self.selected_filter = None
            self.temp_frequencies = {}

    def on_back(self, data=None):
        """ Handle back events """
        if self.selected_filter is not None:
            # Cancel the selection and reset temporary frequencies
            self.selected_filter = None
            self.temp_frequencies = {}

    def adjust_frequency(self, direction):
        """ Helper method to adjust frequency based on direction ('left' or 'right') """
        if self.selected_filter is not None:
            # Map selected filter to the corresponding frequency key
            filter_to_key = {
                0: 'ch_1_hpf',
                1: 'ch_1_lpf',
                2: 'ch_2_hpf',
                3: 'ch_2_lpf'
            }
            key = filter_to_key[self.selected_filter]
            step = 10  # Frequency adjustment step
            if direction == 'right':
                self.temp_frequencies[key] += step
            elif direction == 'left':
                self.temp_frequencies[key] -= step

    def on_right(self, data=None):
        """ Handle right events """
        if self.selected_filter is not None:
            self.adjust_frequency('right')
        else:
            self.update_cursor_position('right')

    def on_left(self, data=None):
        """ Handle left events """
        if self.selected_filter is not None:
            self.adjust_frequency('left')
        else:
            self.update_cursor_position('left')