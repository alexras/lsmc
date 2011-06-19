from instrument import Instrument

# Max. length of a "word"
WORD_LENGTH = 0x20

# Number of "words" in the speech instrument
NUM_WORDS = 42

# Max. length of a word name
WORD_NAME_LENGTH = 4

EMPTY_WORD = [0] * WORD_LENGTH

class WordNameList(object):
    def __init__(self, word_names):
        self.word_names = word_names

    def __getitem__(self, item):
        return ''.join([chr(x) for x in self.word_names[item] if x != 0])\
            .ljust(WORD_NAME_LENGTH)

    def __setitem__(self, item, value):
        item_chars = [ord(x) for x in value]

        self.word_names[item] = item_chars

class SpeechInstrument(Instrument):
    def __init__(self):
        super(SpeechInstrument,self).__init__()

        # Speech instrument is always allocated
        self.allocated = True

        self.raw_words = []
        self.raw_word_names = []

        self._word_names = WordNameList(self.raw_word_names)

    @property
    def words(self):
        return self.raw_words

    @property
    def word_names(self):
        return self._word_names

    def as_dict(self):
        dump_dict = {}

        for i in xrange(NUM_WORDS):
            if self.words[i] != EMPTY_WORD:
                dump_dict[self.word_names[i]] = {
                    "index" : i,
                    "data" : self.words[i]}

        return dump_dict

    def load(self, filename):
        fp = open(filename, 'r')

        jsonObj = json.load(fp)

        for name, fields in jsonObj:
            index = fields["index"]

            self.word_names[index] = name
            self.words[index] = fields["data"]

