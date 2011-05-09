# Binary data for default instrument
DEFAULT = [0xa8, 0, 0, 0xff, 0, 0, 3, 0, 0, 0xd0, 0, 0, 0, 0xf3, 0, 0]

# Max. number of parameters per instrument
NUM_PARAMS = 16

class Instrument(object):
    def __init__(self):
        self.allocated = False
        self.name = None

class SpeechInstrument(object):
    def __init__(self):
        self.words = []
        self.word_names = []
        self.allocated = False
