import json
import utils

# Binary data for default instrument
DEFAULT = [0, 0xa8, 0, 0, 0xff, 0, 0, 3, 0, 0, 0xd0, 0, 0, 0xf3, 0, 0]

# Max. number of parameters per instrument
NUM_PARAMS = 16

# Max. instrument name length
NAME_LENGTH = 5

class InstrumentProperty(object):
    def __init__(self, byte, start_bit = 0, end_bit = 7):
        self.byte = byte
        self.start_bit = start_bit
        self.end_bit = end_bit

    def prop_getter(self, obj):
        return utils.extract_bits(obj.params[self.byte], self.start_bit,
                                  self.end_bit)

    def prop_setter(self, obj, value):
        obj.params[self.byte] = utils.inject_bits(
            obj.params[self.byte],
            value, self.start_bit, self.end_bit)

class Instrument(object):
    def __init__(self):
        self._allocated = False
        self._name = None
        self.params = None
        self.table = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):

        if value == None:
            self._name = None
        elif type(value) == list:
            value = utils.strip_nulls(''.join([chr(x) for x in value]))

            if len(value) == 0:
                self._name = None
            else:
                self._name = value
        else:
            self._name = utils.strip_nulls(value)

    @property
    def allocated(self):
        return self._allocated

    @allocated.setter
    def allocated(self, value):
        self._allocated = bool(value)

    @property
    def instrument_type(self):
        instr_type_byte = self.params[0]

        if instr_type_byte == 0:
            # Pulse instrument
            pass
        elif instr_type_byte == 1:
            # Wave instrument
            pass
        elif instr_type_byte == 2:
            # Kit instrument
            pass
        elif instr_type_byte == 3:
            # Noise instrument
            pass

    def __eq__(self, other):
        return type(self) == type(other) and self.params == other.params

    def __ne__(self, other):
        return not self.__eq__(other)

    def dump(self, filename):
        assert self.allocated, "Shouldn't be saving an unallocated instrument"

        fp = open(filename, 'w')

        dump_dict = {
            "name" : self.name,
            "raw_params" : self.params,
            }

        json.dump(dump_dict, fp)
        fp.close()

    def load(self, filename):
        fp = open(filename, 'r')

        jsonObj = json.load(fp)

        self.name = jsonObj["name"]
        self.params = jsonObj["raw_params"]

        fp.close()

class SpeechInstrument(object):
    def __init__(self):
        self.words = []
        self.word_names = []
        self.allocated = False
