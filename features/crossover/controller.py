from features.crossover.service import CrossoverService

class TwoWayCrossover():
    MAX_CURSOR_POSITION = 3
    CURSOR_SYMBOL = '>'
    DEFAULT_CUTOFF_1 = (30, 500) # Default for channel 1
    DEFAULT_CUTOFF_2 = (500, 20 * 1000) # Default for channel 2

    def __init__(self, dsp, params, name='2way Crossover', channel_names=['A', 'B']):
        self.name = name
        self.params = self.parse_params(params)
        self.cursor_position = 0
        self.channel_names = channel_names
        self.service = CrossoverService(dsp)
        self.selected_filter = None  # Track which filter is selected for adjustment
        self.temp_frequencies = {}   # Store temporary frequency adjustments
        
        # Load saved frequencies from RTC memory (if any)
        self.load_frequencies_from_rtc()

    def load_frequencies_from_rtc(self):
        """ Load saved frequencies from RTC memory and store them in the object """
        # Load frequencies using the crossover's name as the key
        saved_frequencies = self.service.load_state(self.name)
        print(saved_frequencies)
        if saved_frequencies:
            # If saved frequencies exist, update the DSP and store them in the object
            for head_address, (low_cutoff, high_cutoff) in saved_frequencies.items():
                self.service.set_bandpass_cutoff_frequencies(low_cutoff, high_cutoff, int(head_address))
            self.saved_frequencies = saved_frequencies
        else:
            # If no saved frequencies exist, write default frequencies to the DSP and RTC memory
            self.write_default_frequencies()

    def write_default_frequencies(self):
        """ Write default frequencies to the DSP and RTC memory """
        default_frequencies = {
            str(self.params[0]): self.DEFAULT_CUTOFF_1,
            str(self.params[2]): self.DEFAULT_CUTOFF_2,  
        }
        # Write default frequencies to the DSP
        for head_address, (low_cutoff, high_cutoff) in default_frequencies.items():
            self.service.set_bandpass_cutoff_frequencies(low_cutoff, high_cutoff, int(head_address))
        # Save default frequencies to RTC memory
        self.service.save_state(default_frequencies, self.name)
        # Store default frequencies in the object
        self.saved_frequencies = default_frequencies

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
            0: params[0]['Parameter Address'],  # the head of a 5-coefficient filter
            1: params[5]['Parameter Address'],  # the head of another 5-coefficient filter
            2: params[10]['Parameter Address'],  # the head of another 5-coefficient filter
            3: params[15]['Parameter Address'],  # the head of another 5-coefficient filter
            4: params[20]['Parameter Address'] # NOTE: not used for now
        }

    def format_frequency(self, freq):
        """ Format the frequency to be displayed on the LCD """
        freq = int(freq)
        if freq >= 1000:
            return f"{freq/1000:.1f}k"
        return f"{freq}"
    
    def add_cursor_to_selected_filter(self, frequencies):
        for i in range(len(frequencies)):
            if i == self.cursor_position:
                frequencies[i] = f"{self.CURSOR_SYMBOL}{frequencies[i]}"
        return frequencies
    
    def display(self):
        """ Display the current pair of channels on a 2-line LCD with cursor indication """
        ch_1_lpf, ch_1_hpf = self.saved_frequencies.get(str(self.params[0]))
        ch_2_lpf, ch_2_hpf = self.saved_frequencies.get(str(self.params[2]))
        
        # Use temporary frequencies if a filter is selected
        if self.selected_filter is not None:
            ch_1_lpf = self.temp_frequencies.get('ch_1_lpf', ch_1_lpf)
            ch_1_hpf = self.temp_frequencies.get('ch_1_hpf', ch_1_hpf)
            ch_2_lpf = self.temp_frequencies.get('ch_2_lpf', ch_2_lpf)
            ch_2_hpf = self.temp_frequencies.get('ch_2_hpf', ch_2_hpf)
        
        # Map cursor positions to frequencies
        frequencies = [self.format_frequency(f) for f in [ch_1_lpf, ch_1_hpf, ch_2_lpf, ch_2_hpf]]
        frequencies = self.add_cursor_to_selected_filter(frequencies)
            
        line1 = f"{self.channel_names[0]}:{frequencies[0]}-{frequencies[1]} Hz"
        line2 = f"{self.channel_names[1]}:{frequencies[2]}-{frequencies[3]} Hz"
        
        return f"{line1}\n{line2}"

    def set_frequency(self, low_cutoff, high_cutoff, head_address):
        """ Set the cutoff frequencies for a specific channel and save to RTC memory """
        self.service.set_bandpass_cutoff_frequencies(low_cutoff, high_cutoff, head_address)
       
        # Update the saved frequencies in the object
        self.saved_frequencies[str(head_address)] = (low_cutoff, high_cutoff)

        # Save the updated frequencies to RTC memory
        self.service.save_state(self.saved_frequencies, self.name)

    def on_click(self, data=None, navigator=None):
        """ Handle click events """
        if self.selected_filter is None:
            # Select the filter for adjustment
            self.selected_filter = self.cursor_position
            # Initialize temporary frequencies
            ch_1_lpf, ch_1_hpf = self.saved_frequencies.get(str(self.params[0]))
            ch_2_lpf, ch_2_hpf = self.saved_frequencies.get(str(self.params[2]))
            self.temp_frequencies = {
                'ch_1_lpf': ch_1_lpf,
                'ch_1_hpf': ch_1_hpf,
                'ch_2_lpf': ch_2_lpf,
                'ch_2_hpf': ch_2_hpf
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
            
            print(self.temp_frequencies)

            selected_head_address_index = 0 if self.selected_filter <= 1 else 2

            self.set_frequency(
                self.temp_frequencies[low_key],
                self.temp_frequencies[high_key],
                self.params[selected_head_address_index]
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
            return True
        return False # Allow Navigator to go back

    def adjust_frequency(self, direction):
        """ Helper method to adjust frequency based on direction ('left' or 'right') """
        if self.selected_filter is not None:
            # Map selected filter to the corresponding frequency key
            filter_to_key = {
                0: 'ch_1_lpf',
                1: 'ch_1_hpf',
                2: 'ch_2_lpf',
                3: 'ch_2_hpf'
            }
            key = filter_to_key[self.selected_filter]
            step = 10  if self.temp_frequencies[key] < 1000 else 100 # move faster if frequency is higher
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