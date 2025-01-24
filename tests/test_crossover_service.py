from external.sigma.sigma_dsp.dsp_processor import DspNumber
from features.crossover.service import CrossoverService        

# Mock ParameterRAM class
class MockParameterRAM:
    def __init__(self):
        self.data = {}

    def write(self, bytes_array, address):
        # Simulate writing to parameter RAM
        self.data[address] = bytes_array

    def read(self, byte_size, address):
        # Simulate reading from parameter RAM
        return self.data.get(address, b'\x00' * byte_size)

# Mock DSP class
class MockDSP:
    def __init__(self):
        self.DspNumber = DspNumber
        self.parameter_ram = MockParameterRAM()

# Initialize mock DSP and service
mock_dsp = MockDSP()
service = CrossoverService(mock_dsp)

# Test calculate_lowpass_coefficients
def test_calculate_lowpass_coefficients():
    lowpass_coeffs = service.calculate_lowpass_coefficients(1000, 1.0)
    print("Lowpass Coefficients:", lowpass_coeffs)
    assert isinstance(lowpass_coeffs, dict), "Lowpass coefficients should be a dictionary"
    assert "B0" in lowpass_coeffs, "Lowpass coefficients should contain B0"
    print("test_calculate_lowpass_coefficients passed!")

# Test calculate_highpass_coefficients
def test_calculate_highpass_coefficients():
    highpass_coeffs = service.calculate_highpass_coefficients(1000, 1.0)
    print("Highpass Coefficients:", highpass_coeffs)
    assert isinstance(highpass_coeffs, dict), "Highpass coefficients should be a dictionary"
    assert "B0" in highpass_coeffs, "Highpass coefficients should contain B0"
    print("test_calculate_highpass_coefficients passed!")

# Test calculate_bandpass_coefficients
def test_calculate_bandpass_coefficients():
    highpass_coeffs, lowpass_coeffs = service.calculate_bandpass_coefficients(500, 2000)
    print("Bandpass Highpass Coefficients:", highpass_coeffs)
    print("Bandpass Lowpass Coefficients:", lowpass_coeffs)
    assert isinstance(highpass_coeffs, dict), "Bandpass highpass coefficients should be a dictionary"
    assert isinstance(lowpass_coeffs, dict), "Bandpass lowpass coefficients should be a dictionary"
    print("test_calculate_bandpass_coefficients passed!")

# Test set_bandpass_cutoff_frequencies
def test_set_bandpass_cutoff_frequencies():
    service.set_bandpass_cutoff_frequencies(500, 2000, 0x1000)
    print("Parameter RAM after set_bandpass_cutoff_frequencies:", mock_dsp.parameter_ram.data)
    assert 0x1000 in mock_dsp.parameter_ram.data, "Data should be written to address 0x1000"
    print("test_set_bandpass_cutoff_frequencies passed!")

# Test extract_lowpass_cutoff_frequency
def test_extract_lowpass_cutoff_frequency():
    B0, B1, A1, B2, A2 = 0.5, 0.0, 0.5, 0.0, 0.0
    low_cutoff = service.extract_lowpass_cutoff_frequency(B0, B1, A1, B2, A2)
    print("Extracted Lowpass Cutoff Frequency:", low_cutoff)
    assert isinstance(low_cutoff, float), "Lowpass cutoff frequency should be a float"
    print("test_extract_lowpass_cutoff_frequency passed!")

# Test extract_highpass_cutoff_frequency
def test_extract_highpass_cutoff_frequency():
    B0, B1, A1, B2, A2 = 0.5, 0.0, 0.5, 0.0, 0.0
    high_cutoff = service.extract_highpass_cutoff_frequency(B0, B1, A1, B2, A2)
    print("Extracted Highpass Cutoff Frequency:", high_cutoff)
    assert isinstance(high_cutoff, float), "Highpass cutoff frequency should be a float"
    print("test_extract_highpass_cutoff_frequency passed!")

# Test extract_bandpass_cutoff_frequencies
def test_extract_bandpass_cutoff_frequencies():
    mock_dsp.parameter_ram.write(b'\x00\x00\x00\x01' * 5, 0x2000)  # Simulate writing coefficients
    mock_dsp.parameter_ram.write(b'\x00\x00\x00\x01' * 5, 0x3000)
    low_cutoff, high_cutoff = service.extract_bandpass_cutoff_frequencies(0x2000, 0x3000)
    print("Extracted Bandpass Cutoff Frequencies:", low_cutoff, high_cutoff)
    assert isinstance(low_cutoff, float), "Low cutoff frequency should be a float"
    assert isinstance(high_cutoff, float), "High cutoff frequency should be a float"
    print("test_extract_bandpass_cutoff_frequencies passed!")


def run_all_tests():
    """Run all test functions."""
    print("Running all tests...\n")

    # Run each test function
    test_calculate_lowpass_coefficients()
    test_calculate_highpass_coefficients()
    test_calculate_bandpass_coefficients()
    test_set_bandpass_cutoff_frequencies()
    test_extract_lowpass_cutoff_frequency()
    test_extract_highpass_cutoff_frequency()
    test_extract_bandpass_cutoff_frequencies()

    print("\nAll tests passed!")

# Run all tests
if __name__ == "__main__":
    run_all_tests()