# Signed values are converted with two's compliment.
# https://en.wikipedia.org/wiki/Single-precision_floating-point_format
# https://en.wikipedia.org/wiki/Single-precision_floating-point_format
# https://docs.python.org/3/library/struct.html

from math import ceil



class Number:
    N_BITS_A = 9
    N_BITS_B = 23
    LIMIT = 1 << (N_BITS_A - 1)

    N_BITS = N_BITS_A + N_BITS_B
    N_BITS_INTEGER = N_BITS_A
    N_BYTES = ceil(N_BITS / 8)
    INT_FORMAT = (N_BITS, 0)
    FLOAT_FORMAT = (N_BITS_INTEGER, N_BITS - N_BITS_INTEGER)


    def __init__(self, value, n_bits_A = None, n_bits_B = None):
        self.n_bits_A = self.N_BITS_A if n_bits_A is None else n_bits_A
        self.n_bits_B = self.N_BITS_B if n_bits_B is None else n_bits_B
        self.limit_guard(value, self.n_bits_A)

        self.set_value(value)


    def set_value(self, value):
        cased_value = self.type(value)

        if cased_value != value:
            print(f'Warning: {value} is truncated to {cased_value}.')
            assert isinstance(value, self.type), f'{value} needs to be type {self.type}'

        else:
            self._value = cased_value
            return self


    @classmethod
    def limit_guard(cls, value, n_bits):
        limit = 1 << (n_bits - 1)
        assert - limit <= value < limit, f'Need {-limit} <= value < {limit}, current: {value}'


    @classmethod
    def from_bits(cls, bits, n_bits_A = None, n_bits_B = None):
        return cls(cls.bits_to_value(bits, n_bits_A, n_bits_B), n_bits_A, n_bits_B)


    @classmethod
    def from_bytes(cls, AB_bytes, n_bits_A = None, n_bits_B = None):
        return cls(cls.bytes_to_value(AB_bytes, n_bits_A, n_bits_B), n_bits_A, n_bits_B)


    @classmethod
    def bits_to_value(cls, bits, n_bits_A = None, n_bits_B = None):
        n_bits_A = cls.N_BITS_A if n_bits_A is None else n_bits_A
        n_bits_B = cls.N_BITS_B if n_bits_B is None else n_bits_B

        sign_mask = 1 << (n_bits_A + n_bits_B - 1)
        denominator = 1 << n_bits_B
        numerator = (bits & (sign_mask - 1)) - \
                    (bits & (sign_mask - 0))

        num_type = int if n_bits_B == 0 else float

        return num_type(numerator / denominator)


    @classmethod
    def bytes_to_value(cls, AB_bytes, n_bits_A = None, n_bits_B = None):
        bits = int.from_bytes(AB_bytes, 'big')  # for MicroPython
        # bits = int.from_bytes(AB_bytes, byteorder = 'big', signed = False)
        return cls.bits_to_value(bits, n_bits_A, n_bits_B)


    @classmethod
    def to_bits(cls, value, n_bits_A = None, n_bits_B = None):
        n_bits_A = cls.N_BITS_A if n_bits_A is None else n_bits_A
        n_bits_B = cls.N_BITS_B if n_bits_B is None else n_bits_B

        cls.limit_guard(value, n_bits_A)

        denominator = 1 << n_bits_B
        numerator = int(value * denominator)

        return numerator + 2 ** (n_bits_A + n_bits_B) if numerator < 0 else numerator


    @classmethod
    def to_bytes(cls, value, n_bits_A = None, n_bits_B = None):
        n_bits_A = cls.N_BITS_A if n_bits_A is None else n_bits_A
        n_bits_B = cls.N_BITS_B if n_bits_B is None else n_bits_B

        bits = cls.to_bits(value, n_bits_A, n_bits_B)

        return bits.to_bytes(ceil((n_bits_A + n_bits_B) / 8), 'big')  # for MicroPython
        # return bits.to_bytes(length = ceil((n_bits_A + n_bits_B) / 8),
        #                      byteorder = 'big',
        #                      signed = False)


    @property
    def value(self):
        cased_value = self.type(self._value)

        if cased_value != self._value:
            print(f'Warning: {self._value} is truncated to {cased_value}.')

        self._value = cased_value
        return self._value


    @property
    def type(self):
        return int if self.n_bits_B == 0 else float


    def to_integer(self):
        self._value = int(self.value)
        self.n_bits_A = self.n_bits_A + self.n_bits_B
        self.n_bits_B = 0


    def to_float(self):
        self._value = float(self.value)
        self.n_bits_A = self.N_BITS_A
        self.n_bits_B = self.N_BITS_B


    @property
    def bits(self):
        return self.to_bits(self.value, self.n_bits_A, self.n_bits_B)


    @property
    def bytes(self):
        return self.to_bytes(self.value, self.n_bits_A, self.n_bits_B)


    @property
    def size(self):
        return len(self.bytes)



class Float(Number):
    pass



class SignedInteger(Number):
    N_BITS_A = 32
    N_BITS_B = 0
    LIMIT = 1 << (N_BITS_A - 1)


    @classmethod
    def bits_to_value(cls, bits, n_bits_A = None, _ = None):
        return int(super().bits_to_value(bits, n_bits_A, None))