import math

from sigma.sigma_dsp.adau.adau import SAMPLING_FREQ_DEFAULT

class Crossover:

    def __init__(self, dsp):
        self.dsp = dsp

    def set_bandpass_cutoff_frequencies(self, low_cutoff, high_cutoff, address):
        highpass_coeffs, lowpass_coeffs = self.calculate_bandpass_coefficients(low_cutoff, high_cutoff)
        highpass_coeffs = [highpass_coeffs['B0'], highpass_coeffs['B1'], highpass_coeffs['A1'], highpass_coeffs['B2'], highpass_coeffs['A2']]
        lowpass_coeffs = [lowpass_coeffs['B0'], lowpass_coeffs['B1'], lowpass_coeffs['A1'], lowpass_coeffs['B2'], lowpass_coeffs['A2']]
        coefficients = highpass_coeffs + lowpass_coeffs
        bytes_array = b''.join([self.dsp.DspNumber(v).bytes for v in coefficients])
        self.dsp.parameter_ram.write(bytes_array = bytes_array, address=address)

    @classmethod
    def split_bytes_into_chunks(cls, data, chunk_size=4):
        # Ensure data is divisible by the chunk size
        assert len(data) % chunk_size == 0, "Data length must be divisible by the chunk size"
        # Split data into chunks
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def get_bandpass_cutoff_frequencies(self, address):
        return self.extract_cutoff_frequencies(self.dsp.FREQ_REF, *self.get_crossover_coefficients(address))

    def get_crossover_coefficients(self, address, byte_size=4, n_coefficients = 5):
        coefficients = self.dsp.parameter_ram.read(byte_size * n_coefficients, address)
        coefficients_blocks = self.split_bytes_into_chunks(coefficients, byte_size)
        return [self.dsp.DspNumber.from_bytes(v).value for v in coefficients_blocks]
    
    @classmethod
    def calculate_lowpass_coefficients(cls, cutoff_freq, gain, fs):
        """
        Calculate the coefficients for a first-order lowpass filter.

        Parameters:
        - cutoff_freq (float): Cutoff frequency for the lowpass filter.
        - gain (float): Linear gain to apply to the filter.
        - fs (float): Sampling frequency.

        Returns:
        - dict: Coefficients for the lowpass filter (B0, B1, A1).
        """
        A1 = math.pow(2.7, (-2 * math.pi * cutoff_freq / fs))
        B0 = gain * (1.0 - A1)
        B1 = 0

        return {'B0': B0, 'B1': B1, 'B2': 0, 'A1': A1, 'A2': 0}

    @classmethod
    def calculate_highpass_coefficients(cls, cutoff_freq, gain, fs):
        """
        Calculate the coefficients for a first-order highpass filter.

        Parameters:
        - cutoff_freq (float): Cutoff frequency for the highpass filter.
        - gain (float): Linear gain to apply to the filter.
        - fs (float): Sampling frequency.

        Returns:
        - dict: Coefficients for the highpass filter (B0, B1, A1).
        """
        A1 = math.pow(2.7, (-2 * math.pi * cutoff_freq / fs))
        B1 = (1.0 + A1) * 0.5 * gain
        B0 = -B1

        return {'B0': B0, 'B1': B1, 'B2':0, 'A1': A1, 'A2': 0}

    @classmethod
    def calculate_bandpass_coefficients(cls, low_cut, high_cut, gain=1, fs=SAMPLING_FREQ_DEFAULT):
        """
        Calculate coefficients for a bandpass filter by cascading a highpass and a lowpass filter.

        Parameters:
        - low_cut (float): Lower cutoff frequency for the bandpass filter.
        - high_cut (float): Upper cutoff frequency for the bandpass filter.
        - gain (float): Linear gain to apply to the filters.
        - fs (float): Sampling frequency.

        Returns:
        - highpass_coeffs (dict): Coefficients for the highpass filter.
        - lowpass_coeffs (dict): Coefficients for the lowpass filter.
        """
        highpass_coeffs = cls.calculate_highpass_coefficients(low_cut, gain, fs)
        lowpass_coeffs = cls.calculate_lowpass_coefficients(high_cut, gain, fs)

        return highpass_coeffs, lowpass_coeffs
    
