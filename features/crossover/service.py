import json
import math
import esp32

from external.sigma.sigma_dsp.adau.adau import SAMPLING_FREQ_DEFAULT

class CrossoverService:
    crossover_memory_namespace = "crossover"

    def __init__(self, dsp):
        self.dsp = dsp
        self.calculate_highpass_filter_coefficients = self.calculate_second_order_butterworth_highpass_coefficients
        self.calculate_lowpass_filter_coefficients = self.calculate_second_order_butterworth_lowpass_coefficients

    @classmethod
    def save_state(cls, cutoffs, filter_id):
        """
        Save cutoff frequencies to NVS.
        """
        try:
            nvs = esp32.NVS(cls.crossover_memory_namespace)
            # Convert cutoffs to bytes
            data = json.dumps({filter_id: cutoffs}).encode('utf-8')
            nvs.set_blob(filter_id, data)  # Store under the filter_id key
            nvs.commit()  # Save changes
        except Exception as e:
            print("Error saving to NVS:", e)

    @classmethod
    def load_state(cls, filter_id):
        try:
            nvs = esp32.NVS("crossover")
            
            # Step 1: Get the size of the blob
            size = nvs.get_blob(filter_id, bytearray(0))  # Pass empty buffer to get size
            if size is None:
                return None  # Key does not exist
            
            # Step 2: Allocate a buffer of the exact size
            data = bytearray(size)
            
            # Step 3: Read the blob into the buffer
            nvs.get_blob(filter_id, data)
            
            # Step 4: Decode and parse JSON
            decoded_data = json.loads(data.decode('utf-8'))
            return decoded_data.get(filter_id)
        except Exception as e:
            print("Error loading from NVS:", e)
            return None

    
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

    @staticmethod
    def split_bytes_into_chunks(data, chunk_size=4):
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

    @staticmethod
    def convolve_coefficients(coeffs1, coeffs2):
        """
        Convolve two sets of filter coefficients (polynomial multiplication).

        Parameters:
        - coeffs1 (list): Coefficients of the first polynomial.
        - coeffs2 (list): Coefficients of the second polynomial.

        Returns:
        - list: Convolved coefficients.
        """
        result = [0] * (len(coeffs1) + len(coeffs2) - 1)
        for i in range(len(coeffs1)):
            for j in range(len(coeffs2)):
                result[i + j] += coeffs1[i] * coeffs2[j]
        return result

    @staticmethod
    def cascade_two_filters(B1, A1, B2, A2):
        """
        Cascade two filters into a single filter.

        Parameters:
        - B1 (list): Numerator coefficients of the first filter [B0_1, B1_1, ..., Bn_1].
        - A1 (list): Denominator coefficients of the first filter [A0_1, A1_1, ..., An_1].
        - B2 (list): Numerator coefficients of the second filter [B0_2, B1_2, ..., Bm_2].
        - A2 (list): Denominator coefficients of the second filter [A0_2, A1_2, ..., Am_2].

        Returns:
        - B (list): Numerator coefficients of the resulting cascaded filter.
        - A (list): Denominator coefficients of the resulting cascaded filter.
        """
        # Convolve the numerators and denominators
        B = convolve_coefficients(B1, B2)
        A = convolve_coefficients(A1, A2)

        return B, A

    @staticmethod
    def calculate_first_order_lowpass_coefficients(cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
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

    @staticmethod
    def calculate_first_order_butterworthhighpass_coefficients(cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
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

    @staticmethod
    def calculate_second_order_butterworth_lowpass_coefficients(cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
        """
        Calculate the coefficients for a 2nd order lowpass Butterworth filter.

        Parameters:
        - cutoff_freq (float): Cutoff frequency for the lowpass filter.
        - gain (float): Linear gain to apply to the filter.
        - fs (float): Sampling frequency.

        Returns:
        - dict: Coefficients for the lowpass filter (B0, B1, B2, A1, A2).
        """
        omega = 2 * math.pi * cutoff_freq / fs
        sn = math.sin(omega)
        cs = math.cos(omega)
        alpha = sn / (2 * (1 / math.sqrt(2)))  # Equivalent to sn / sqrt(2)
        a0 = 1 + alpha

        A1 = -(2 * cs) / a0
        A2 = (1 - alpha) / a0
        B1 = (1 - cs) / a0 * (10 ** (gain / 20))
        B0 = B1 / 2
        B2 = B0

        return {'B0': B0, 'B1': B1, 'B2': B2, 'A1': A1, 'A2': A2}

    @staticmethod
    def calculate_second_order_butterworth_highpass_coefficients(cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
        """
        Calculate the coefficients for a 2nd order highpass Butterworth filter.

        Parameters:
        - cutoff_freq (float): Cutoff frequency for the highpass filter.
        - gain (float): Linear gain to apply to the filter.
        - fs (float): Sampling frequency.

        Returns:
        - dict: Coefficients for the highpass filter (B0, B1, B2, A1, A2).
        """
        omega = 2 * math.pi * cutoff_freq / fs
        sn = math.sin(omega)
        cs = math.cos(omega)
        alpha = sn / (2 * (1 / math.sqrt(2)))  # Equivalent to sn / sqrt(2)
        a0 = 1 + alpha

        A1 = -(2 * cs) / a0
        A2 = (1 - alpha) / a0
        B1 = -(1 + cs) / a0 * (10 ** (gain / 20))
        B0 = -B1 / 2
        B2 = B0

        return {'B0': B0, 'B1': B1, 'B2': B2, 'A1': A1, 'A2': A2}

    
    def calculate_bandpass_coefficients(self, low_cut, high_cut, gain=1, fs=SAMPLING_FREQ_DEFAULT):
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
        highpass_coeffs = self.calculate_highpass_filter_coefficients(high_cut, gain, fs)
        lowpass_coeffs = self.calculate_lowpass_filter_coefficients(low_cut, gain, fs)

        return highpass_coeffs, lowpass_coeffs
    
