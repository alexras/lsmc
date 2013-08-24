from instrument import Instrument

# Max. length of a "word"
WORD_LENGTH = 0x20

# Number of "words" in the speech instrument
NUM_WORDS = 42

# Max. length of a word name
WORD_NAME_LENGTH = 4

EMPTY_WORD = [0] * WORD_LENGTH

def word_cleanup(word):
    return ''.join([chr(x) for x in word if x != 0]).ljust(WORD_NAME_LENGTH)

class SpeechInstrument(object):
    def __init__(self, words, word_names):
        self.words = {}
        self.word_names = {}

        for i, word in enumerate(words):
            if word != EMPTY_WORD:
                self.words[i] = word
                self.word_names[i] = word_cleanup(word_names[i])

    def as_dict(self):
        dump_dict = {}

        for i in words:
            dump_dict[self.word_names[i]] = {
                "index": i,
                "data": self.words[i]
            }

        return dump_dict

    def load(self, filename):
        fp = open(filename, 'r')

        jsonObj = json.load(fp)

        for name, fields in jsonObj:
            index = fields["index"]

            self.word_names[index] = name
            self.words[index] = fields["data"]
