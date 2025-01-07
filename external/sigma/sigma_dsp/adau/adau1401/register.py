import json
import math
from array import array



def _elements_by_attr(elements, attr):
    keyed_elements = {getattr(e, attr): e for e in elements}
    assert len(list(keyed_elements.keys())) == len(elements), '{} are not unique.'.format(attr)

    return keyed_elements



class RegistersMap:

    def __init__(self, name, description = None, registers = None):
        self.name = name
        self.description = description
        self.registers = registers

        elements_names = [ele.name for reg in self._registers for ele in reg._elements]
        self.duplicated_element_names = tuple(sorted(n for n in set(elements_names) if elements_names.count(n) > 1))


    @property
    def registers(self):
        return self._registers_dict


    @registers.setter
    def registers(self, registers):
        self._registers = registers or []
        self._registers_dict = _elements_by_attr(self._registers, 'name')
        self._registers_by_address = _elements_by_attr(self._registers, 'address')
        self._elements = {e.name: {'element': e, 'register': reg} for reg in self._registers for e in reg._elements}


    @property
    def registers_by_address(self):
        return self._registers_by_address


    @property
    def elements(self):
        return self._elements


    @property
    def has_same_name_elements(self):
        return len(self.duplicated_element_names) > 0


    def value_of_element(self, element_name):
        return self.elements[element_name]['element'].value


    def register_address_of_element(self, element_name):
        return self.elements[element_name]['register'].address


    def set_element_value(self, element_name, value):
        d = self.elements[element_name]
        d['element'].value = value
        return d['register']


    def write_element(self, element_name, value):
        d = self.elements[element_name]
        element = d['element']
        register = d['register']
        element.value = value
        return register, element


    @property
    def values(self):
        return [reg.value for reg in self._registers]


    @property
    def address_name_values(self):
        return sorted([(reg.address, reg.name, reg.value) for reg in self._registers])


    @property
    def addressed_values(self):
        return sorted([(reg.address, reg.value) for reg in self._registers])


    def load_values_by_name(self, named_values):
        for (reg_name, value) in named_values:
            self.registers[reg_name].load_value(value)


    def load_values(self, addressed_values):
        for (address, value) in addressed_values:
            try:
                self.registers_by_address[address].load_value(value)
            except KeyError as e:
                print('There is no register as address {}.'.format(e))


    def read_file(self, file_name):
        addressed_values = []

        with open(file_name) as f:
            lines = f.readlines()

            for line in lines:
                if not line.startswith('#'):
                    address, value = line.replace('h', '').split(',')
                    addressed_values.append((int(address), int(value, 16)))

        return addressed_values


    def load_file(self, file_name):
        self.load_values(self.read_file(file_name))


    def save_to_file(self, file_name):
        with open(file_name, 'wt') as f:
            for address, value in self.addressed_values:
                f.write('{}, {}\n'.format(address, hex(value)))


    def compare_values_sets(self, set_1, set_2):
        import numpy as np

        address_max = max([a for a, _ in set_1] + [a for a, _ in set_2])
        addresses = range(address_max + 1)

        comparison = np.full((4, len(addresses)), np.nan)
        comparison[0] = addresses

        for i in range(2):
            for a, v in (set_1, set_2)[i]:
                comparison[i + 1, a] = v

        comparison = np.delete(comparison, np.argwhere(np.isnan(comparison[1]) & np.isnan(comparison[2])), axis = 1)
        comparison[-1] = (comparison[1] != comparison[2])

        return comparison.T


    def compare_values_sets_pd(self, set_1, set_2):
        import pandas as pd

        self.load_values(set_1)
        df1 = self.df

        self.load_values(set_2)
        df2 = self.df

        df = pd.merge(df1, df2, how = 'outer', on = ['address', 'element_name'], suffixes = ('', '_2'))
        df = df[['register', 'address', 'default_value', 'element_name', 'idx_lowest_bit', 'n_bits', 'read_only',
                 'value', 'value_2']]
        df['different'] = (df.value != df.value_2).astype(int)
        df.index = range(len(df))

        return df


    def reset(self):
        for register in self._registers:
            register.reset()


    def print(self, as_hex = False):
        for register in self._registers:
            register.print(as_hex = as_hex)


    def loads(self, json_string):
        rm_attrs = json.loads(json_string)

        reg_map = RegistersMap('')
        reg_map.name = rm_attrs['name']
        reg_map.description = rm_attrs['description']
        reg_map.registers = [Register.loads(json.dumps(reg_attrs)) for reg_attrs in rm_attrs['registers']]
        return reg_map


    def dumps(self):
        d = {'name'       : self.name,
             'description': self.description,
             'registers'  : [json.loads(r.dumps()) for r in self._registers]}

        return json.dumps(d)


    @property
    def df(self):

        try:
            import pandas as pd

            df = pd.concat([r.df for r in self._registers])
            df.index = range(len(df))

            return df

        except ImportError:
            print('Need Pandas.')



class Register:

    def __init__(self, name, code_name = None, address = None, description = None, elements = None, default_value = 0):
        self.name = name
        self.code_name = code_name or name
        self.address = address
        self.description = description
        self.elements = elements
        self.default_value = default_value


    @property
    def elements(self):
        return self._elements_dict


    @elements.setter
    def elements(self, elements):
        self._elements = elements or []
        self._elements_dict = _elements_by_attr(self._elements, 'name')


    @property
    def n_bits(self):
        return sum([e.n_bits for e in self._elements])


    @property
    def n_bytes(self):
        return math.ceil(self.n_bits / 8)


    @property
    def value(self):
        return int(sum([e.shifted_value for e in self._elements]))


    @property
    def bytes(self):
        return array('B', self.value.to_bytes(self.n_bytes, 'big'))


    def load_value(self, value):
        for e in self._elements:
            e.load_value(value)


    def reset(self):
        self.load_value(self.default_value)


    def print(self, as_hex = False):
        len_name_field = max([len(e.name) for e in self._elements] + [0])
        print('\n{:<{}s}:  {}'.format('<< ' + self.name + ' >>', len_name_field + 7,
                                      (hex(self.value), bin(self.value))))
        for e in self._elements:
            print('{:<{}s}:  {}'.format('[ ' + e.name + ' ]', len_name_field + 5,
                                        (hex(e.value), bin(e.value)) if as_hex else e.value))
        return len_name_field


    @classmethod
    def loads(cls, json_string):
        reg_attrs = json.loads(json_string)

        reg = Register('')
        reg.name = reg_attrs['name']
        reg.code_name = reg_attrs['code_name']
        reg.address = reg_attrs['address']
        reg.description = reg_attrs['description']
        reg.default_value = reg_attrs['default_value']
        reg.elements = [Element(**element_attrs) for element_attrs in reg_attrs['elements']]
        return reg


    def dumps(self):
        d = {'name'         : self.name,
             'code_name'    : self.code_name,
             'address'      : self.address,
             'description'  : self.description,
             'default_value': self.default_value,
             'elements'     : [json.loads(e.dumps()) for e in self._elements]}

        return json.dumps(d)


    @property
    def df(self):

        try:
            import pandas as pd

            reg_dict = json.loads(self.dumps())
            df = pd.DataFrame(reg_dict['elements'])

            df['register'] = reg_dict['name']
            df['address'] = reg_dict['address']
            df['default_value'] = reg_dict['default_value']
            df['register_description'] = reg_dict['description']

            df = df[['register', 'address', 'default_value', 'register_description',
                     'name', 'description', 'idx_lowest_bit', 'n_bits', 'value', 'read_only']]
            df.rename(columns = {'name': 'element_name'}, inplace = True)

            return df

        except ImportError:
            print('Need Pandas.')



class Element:

    def __init__(self, name, idx_lowest_bit, n_bits = 1, value = 0, read_only = False, code_name = None,
                 description = None):
        self.name = name
        self.idx_lowest_bit = idx_lowest_bit
        self.n_bits = n_bits
        self._value = value
        self.read_only = read_only
        self.code_name = code_name or name
        self.description = description


    @property
    def value(self):
        return self._value


    @value.setter
    def value(self, value):
        if not self.read_only:
            self._value = value


    @classmethod
    def section_value(cls, value, idx_lowest_bit, n_bits):
        mask = (2 ** n_bits - 1) << idx_lowest_bit
        return (value & mask) >> idx_lowest_bit


    @property
    def mask(self):
        return (2 ** self.n_bits - 1) << self.idx_lowest_bit


    @property
    def shifted_value(self):
        return (self.value << self.idx_lowest_bit) & self.mask


    def load_value(self, value):
        self.value = (value & self.mask) >> self.idx_lowest_bit


    @classmethod
    def loads(cls, json_string):
        attrs = json.loads(json_string)
        return Element(**attrs)


    def dumps(self):
        d = {'name'          : self.name,
             'idx_lowest_bit': self.idx_lowest_bit,
             'n_bits'        : self.n_bits,
             'value'         : self.value,
             'read_only'     : self.read_only,
             'code_name'     : self.code_name,
             'description'   : self.description}

        return json.dumps(d)