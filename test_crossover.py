from controllers.crossover.crossover import Crossover
from sigma.sigma_dsp.adau.adau import SAMPLING_FREQ_DEFAULT
from sigma.sigma_dsp.adau.adau1401.adau1401 import ADAU1401 as ADAU
from sigma.bus.adapters import I2C as SigmaI2C
from machine import I2C, Pin
i2c = I2C(scl=Pin(26), sda=Pin(27), freq=400000)
bus = SigmaI2C(i2c)
dsp = ADAU(bus)
print("I2C Address:", dsp._i2c_address)
crossover = Crossover(dsp, 34)
expected_coefficients = crossover.service.calculate_bandpass_coefficients(
        low_cut=100, high_cut=1000
    )
crossover.service.extract_cutoff_frequencies(SAMPLING_FREQ_DEFAULT, *expected_coefficients)