from features.crossover.controller import TwoWayCrossover
from utils.get_params import get_params

# Mock CrossoverService for testing
class MockCrossoverService:
    def extract_bandpass_cutoff_frequencies(self, filter_1, filter_2):
        return 100, 1000  # Return fixed values for testing

    def set_bandpass_cutoff_frequencies(self, low_cutoff, high_cutoff, head_address):
        pass  # Do nothing for testing


# Test cases
def test_initialization():
    params = get_params()['Crossover1']
    crossover = TwoWayCrossover(None, params)
    assert crossover.name == '2way Crossover', "Initialization failed: name mismatch"
    assert crossover.cursor_position == 0, "Initialization failed: cursor position mismatch"
    assert crossover.selected_filter is None, "Initialization failed: selected_filter not None"
    assert crossover.temp_frequencies == {}, "Initialization failed: temp_frequencies not empty"
    print("test_initialization passed")

def test_update_cursor_position():
    params = get_params()['Crossover1']
    crossover = TwoWayCrossover(None, params)
    
    # Test moving right
    crossover.update_cursor_position('right')
    assert crossover.cursor_position == 1, "Cursor position should be 1 after moving right"
    
    # Test moving left
    crossover.update_cursor_position('left')
    assert crossover.cursor_position == 0, "Cursor position should be 0 after moving left"
    
    # Test wrapping around when moving right past the max position
    crossover.cursor_position = crossover.MAX_CURSOR_POSITION
    crossover.update_cursor_position('right')
    assert crossover.cursor_position == 0, "Cursor position should wrap to 0 after moving right past max"
    
    # Test wrapping around when moving left past the min position
    crossover.cursor_position = 0
    crossover.update_cursor_position('left')
    assert crossover.cursor_position == crossover.MAX_CURSOR_POSITION, "Cursor position should wrap to max after moving left past min"
    print("test_update_cursor_position passed")

def test_display():
    params = get_params()['Crossover1']
    crossover = TwoWayCrossover(None, params)
    crossover.service = MockCrossoverService()
    
    # Test display without any selected filter
    expected_output = "CH1: >100Hz - 1.0kHz\nCH2: 100Hz - 1.0kHz"
    assert crossover.display() == expected_output, "Display output mismatch without selected filter"
    
    # Test display with a selected filter
    crossover.selected_filter = 0
    crossover.temp_frequencies = {'ch_1_hpf': 200, 'ch_1_lpf': 2000}
    expected_output = "CH1: >2.0kHz - 200Hz\nCH2: 100Hz - 1.0kHz"
    assert crossover.display() == expected_output, "Display output mismatch with selected filter"
    print("test_display passed")

def test_on_click():
    params = get_params()['Crossover1']
    crossover = TwoWayCrossover(None, params)
    crossover.service = MockCrossoverService()
    
    # Test selecting a filter
    crossover.cursor_position = 0
    crossover.on_click()
    assert crossover.selected_filter == 0, "Selected filter should be 0"
    assert crossover.temp_frequencies == {
        'ch_1_hpf': 100,
        'ch_1_lpf': 1000,
        'ch_2_hpf': 100,
        'ch_2_lpf': 1000
    }, "Temporary frequencies mismatch after selecting filter"
    
    # Test applying the selected filter
    crossover.on_click()
    assert crossover.selected_filter is None, "Selected filter should be None after applying"
    assert crossover.temp_frequencies == {}, "Temporary frequencies should be empty after applying"
    print("test_on_click passed")

def test_on_back():
    params = get_params()['Crossover1']
    crossover = TwoWayCrossover(None, params)
    crossover.service = MockCrossoverService()
    
    # Test canceling a selection
    crossover.selected_filter = 0
    crossover.temp_frequencies = {'ch_1_hpf': 200, 'ch_1_lpf': 2000}
    crossover.on_back()
    assert crossover.selected_filter is None, "Selected filter should be None after canceling"
    assert crossover.temp_frequencies == {}, "Temporary frequencies should be empty after canceling"
    print("test_on_back passed")

def test_adjust_frequency():
    params = get_params()['Crossover1']
    crossover = TwoWayCrossover(None, params)
    crossover.service = MockCrossoverService()
    
    # Test adjusting frequency to the right
    crossover.selected_filter = 0
    crossover.temp_frequencies = {'ch_1_hpf': 100}
    crossover.adjust_frequency('right')
    assert crossover.temp_frequencies['ch_1_hpf'] == 110, "Frequency should increase by 10 when adjusting right"
    
    # Test adjusting frequency to the left
    crossover.adjust_frequency('left')
    assert crossover.temp_frequencies['ch_1_hpf'] == 100, "Frequency should decrease by 10 when adjusting left"
    print("test_adjust_frequency passed")

def test_on_right():
    params = get_params()['Crossover1']
    crossover = TwoWayCrossover(None, params)
    crossover.service = MockCrossoverService()
    
    # Test moving cursor to the right
    crossover.on_right()
    assert crossover.cursor_position == 1, "Cursor position should be 1 after moving right"
    
    # Test adjusting frequency to the right when a filter is selected
    crossover.selected_filter = 0
    crossover.temp_frequencies = {'ch_1_hpf': 100}
    crossover.on_right()
    assert crossover.temp_frequencies['ch_1_hpf'] == 110, "Frequency should increase by 10 when adjusting right"
    print("test_on_right passed")

def test_on_left():
    params = get_params()['Crossover1']
    crossover = TwoWayCrossover(None, params)
    crossover.service = MockCrossoverService()
    
    # Test moving cursor to the left
    crossover.on_left()
    assert crossover.cursor_position == crossover.MAX_CURSOR_POSITION, "Cursor position should wrap to max after moving left"
    
    # Test adjusting frequency to the left when a filter is selected
    crossover.selected_filter = 0
    crossover.temp_frequencies = {'ch_1_hpf': 100}
    crossover.on_left()
    assert crossover.temp_frequencies['ch_1_hpf'] == 90, "Frequency should decrease by 10 when adjusting left"
    print("test_on_left passed")