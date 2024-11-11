from controllers.crossover.crossover import Crossover
from sigma.sigma_dsp.adau.adau1401.adau1401 import ADAU1401 as ADAU
from sigma.bus.adapters import I2C as SigmaI2C
from machine import I2C, Pin

def test_crossover_coefficients_write_and_read():
    # Set up I2C and DSP
    i2c = I2C(scl=Pin(26), sda=Pin(27), freq=400000)
    bus = SigmaI2C(i2c)
    dsp = ADAU(bus)
    print("I2C Address:", dsp._i2c_address)
    crossover = Crossover(dsp, 34)
    
    # Calculate bandpass coefficients and write to DSP
    expected_coefficients = crossover.service.calculate_bandpass_coefficients(
        low_cut=100, high_cut=1000
    )
    bytes_array = b''.join(crossover.service.dsp.DspNumber(value).bytes for value in expected_coefficients)
    crossover.service.dsp.parameter_ram.write(bytes_array=bytes_array, address=34)
    
    # Read coefficients from DSP
    read_coefficients = crossover.service.get_crossover_coefficients(34)

    # Assertion function
    def assert_coefficients(expected, actual, tolerance=1e-6):
        for i, (exp, act) in enumerate(zip(expected, actual)):
            assert abs(exp - act) <= tolerance, \
                f"Coefficient {i} mismatch: expected {exp:.7f}, got {act:.7f} (tolerance {tolerance})"

    # Test if written coefficients match read coefficients
    assert_coefficients(expected_coefficients, read_coefficients)

# Run the test
test_crossover_coefficients_write_and_read()