class Instrument(object):
    def __init__(self):
        self.allocated = False

class SpeechInstrument(object):
    def __init__(self):
        self.words = []
        self.word_names = []
        self.allocated = False
