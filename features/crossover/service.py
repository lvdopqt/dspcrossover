import json
import math
import esp32

from external.sigma.sigma_dsp.adau.adau import SAMPLING_FREQ_DEFAULT

class CrossoverService:
    crossover_memory_namespace = "crossover"

    def __init__(self, dsp):
        self.dsp = dsp

    def calculate_lowpass_filter_coefficients(self, cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
        return self.calculate_first_order_butterworth_lowpass_coefficients(cutoff_freq, gain, fs)

    def calculate_highpass_filter_coefficients(self, cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
        return self.calculate_first_order_butterworth_highpass_coefficients(cutoff_freq, gain, fs)

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
    def calculate_first_order_butterworth_lowpass_coefficients(cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
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
    def calculate_first_order_butterworth_highpass_coefficients(cutoff_freq, gain, fs=SAMPLING_FREQ_DEFAULT):
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
    
