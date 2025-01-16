import math

from external.sigma.sigma_dsp.adau.adau import SAMPLING_FREQ_DEFAULT

class CrossoverService:

    def __init__(self, dsp):
        self.dsp = dsp

    def set_bandpass_cutoff_frequencies(self, low_cutoff, high_cutoff, address):
        """
        Set the cutoff frequencies for a bandpass filter.
        """
        highpass_coeffs, lowpass_coeffs = self.calculate_bandpass_coefficients(low_cutoff, high_cutoff)
        highpass_coeffs = [highpass_coeffs['B0'], highpass_coeffs['B1'], highpass_coeffs['A1'], highpass_coeffs['B2'], highpass_coeffs['A2']]
        lowpass_coeffs = [lowpass_coeffs['B0'], lowpass_coeffs['B1'], lowpass_coeffs['A1'], lowpass_coeffs['B2'], lowpass_coeffs['A2']]
        coefficients = highpass_coeffs + lowpass_coeffs # 10 coefficients
        bytes_array = b''.join([self.dsp.DspNumber(v).bytes for v in coefficients])
        self.dsp.parameter_ram.write(bytes_array = bytes_array, address=address)

    @classmethod
    def split_bytes_into_chunks(cls, data, chunk_size=4):
        # Ensure data is divisible by the chunk size
        assert len(data) % chunk_size == 0, "Data length must be divisible by the chunk size"
        # Split data into chunks
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def get_crossover_coefficients(self, address, byte_size=4, n_coefficients = 5):
        """
        Get the coefficients for a crossover filter.
        """
        coefficients = self.dsp.parameter_ram.read(byte_size * n_coefficients, address)
        coefficients_blocks = self.split_bytes_into_chunks(coefficients, byte_size)
        return [self.dsp.DspNumber.from_bytes(v).value for v in coefficients_blocks]
    
    @classmethod
    def calculate_lowpass_coefficients(cls, cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
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
    def calculate_highpass_coefficients(cls, cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
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
    def extract_lowpass_cutoff_frequency(cls, B0, B1, A1, B2, A2, fs=SAMPLING_FREQ_DEFAULT):
        """
        Extract the cutoff frequency from lowpass filter coefficients.

        Parameters:
        - fs (float): Sampling frequency
        - B0, B1, A1, B2, A2: Filter coefficients

        Returns:
        - float: Cutoff frequency of the lowpass filter
        """
        # For lowpass: A1 = e^(-2π*fc/fs)
        # Therefore: fc = -fs/(2π) * ln(A1)
        cutoff_freq = -fs/(2 * math.pi) * math.log(A1)
        return cutoff_freq

    @classmethod 
    def extract_highpass_cutoff_frequency(cls, B0, B1, A1, B2, A2, fs=SAMPLING_FREQ_DEFAULT):
        """
        Extract the cutoff frequency from highpass filter coefficients.

        Parameters:
        - fs (float): Sampling frequency
        - B0, B1, A1, B2, A2: Filter coefficients

        Returns:
        - float: Cutoff frequency of the highpass filter
        """
        # For highpass: A1 = e^(-2π*fc/fs)
        # Therefore: fc = -fs/(2π) * ln(A1)
        cutoff_freq = -fs/(2 * math.pi) * math.log(A1)
        return cutoff_freq

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

    @classmethod
    def extract_bandpass_cutoff_frequencies(cls, lpf_address, hpf_address, fs=SAMPLING_FREQ_DEFAULT):
        """
        Extract the cutoff frequencies from bandpass filter coefficients.

        Parameters:
        - lpf_address (int): Address of the lowpass filter.
        - hpf_address (int): Address of the highpass filter.
        - fs (float): Sampling frequency.

        Returns:
        - tuple: (low_cutoff, high_cutoff) frequencies of the bandpass filter
        """
        # Get the 5 coefficients from addresses
        lpf_coeffs = self.get_crossover_coefficients(lpf_address)
        hpf_coeffs = self.get_crossover_coefficients(hpf_address)
        
        # Extract cutoff frequencies using coefficients
        low_cutoff = cls.extract_highpass_cutoff_frequency(
            *hpf_coeffs, fs
        )
        high_cutoff = cls.extract_lowpass_cutoff_frequency(
            *lpf_coeffs, fs
        )
        return low_cutoff, high_cutoff
    
