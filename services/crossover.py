import math

class Crossover:

    def __init__(self, dsp):
        self.dsp = dsp

    @classmethod
    def calculate_bandpass_coefficients(cls, low_cutoff, high_cutoff, fs):
        """
        Calculate biquad filter coefficients for a bandpass filter.

        Parameters:
        - low_cutoff: Lower cutoff frequency (Hz)
        - high_cutoff: Upper cutoff frequency (Hz)
        - fs: Sampling frequency (Hz)

        Returns:
        - b0, b1, a1, b2, a2: Coefficients for the bandpass filter
        """
        # Calculate central frequency and bandwidth
        f0 = (low_cutoff + high_cutoff) / 2
        BW = high_cutoff - low_cutoff

        # Quality factor Q
        Q = f0 / BW

        # Normalized angular frequency
        omega0 = 2 * math.pi * f0 / fs
        sin_omega0 = math.sin(omega0)
        cos_omega0 = math.cos(omega0)

        # Compute alpha for bandwidth adjustment
        alpha = sin_omega0 / (2 * Q)

        # Biquad filter coefficients
        b0 = alpha
        b1 = 0
        b2 = -alpha
        a0 = 1 + alpha
        a1 = -2 * cos_omega0
        a2 = 1 - alpha

        # Normalize coefficients
        b0 /= a0
        b1 /= a0
        b2 /= a0
        a1 /= a0
        a2 /= a0

        # Return coefficients in the specified order
        return b0, b1, a1, b2, a2
    
    @classmethod
    def calculate_allpass_biquad_coefficients(cls, f0, Q, fs):
        """
        Calculate the biquad coefficients for an all-pass filter.
        
        Parameters:
        - f0 : float : Center frequency for the phase shift (Hz)
        - Q : float : Quality factor controlling the width of the phase shift
        - fs : float : Sampling frequency (Hz)
        
        Returns:
        - b0, b1, a1, b2, a2 : float : Coefficients for the all-pass filter
        """
        # Calculate normalized angular frequency
        omega0 = 2 * math.pi * f0 / fs
        alpha = math.sin(omega0) / (2 * Q)

        # Calculate the coefficients for an all-pass filter
        b0 = 1 - alpha
        b1 = -2 * math.cos(omega0)
        b2 = 1 + alpha
        a0 = b2  # We use a0 to normalize
        a1 = b1
        a2 = b0

        # Normalize coefficients by a0
        b0 /= a0
        b1 /= a0
        b2 /= a0
        a1 /= a0
        a2 /= a0

        return b0, b1, a1, b2, a2

    @classmethod
    def extract_cutoff_frequencies(cls, fs, b0, b1, b2, a1, a2):
        """
        Extrai as frequências de corte aproximadas (low_cutoff e high_cutoff) a partir dos coeficientes de um filtro biquad passa-banda.

        Parâmetros:
        - b0, b1, b2, a1, a2: coeficientes do filtro biquad
        - fs: taxa de amostragem (Hz)

        Retorna:
        - low_cutoff, high_cutoff: frequências de corte baixas e altas aproximadas
        """
        # Calcule a frequência angular central normalizada
        omega0 = math.acos(-a1 / 2)  # Aproximação para frequência angular
        f0 = (omega0 * fs) / (2 * math.pi)  # Frequência central em Hz

        # Calcule o fator de qualidade Q
        try:
            alpha = (1 - a2) / (2 * math.sin(omega0))
            Q = 1 / (2 * alpha)
        except ZeroDivisionError:
            return None, None  # Retorne nulo se Q não puder ser calculado devido a uma divisão por zero

        # Calcule a largura de banda e as frequências de corte
        BW = f0 / Q
        low_cutoff = max(0, f0 - BW / 2)  # Garante que as frequências sejam positivas
        high_cutoff = max(0, f0 + BW / 2)

        return low_cutoff, high_cutoff

    def set_bandpass_cutoff_frequencies(self, low_cutoff, high_cutoff, address):
        coefficients = self.calculate_bandpass_coefficients(low_cutoff, high_cutoff, self.dsp.FREQ_REF)
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
        
    
