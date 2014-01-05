from instrument import Instrument
from utils import add_song_data_property

# Max. length of a "word"
WORD_LENGTH = 0x20

# Number of "words" in the speech instrument
NUM_WORDS = 42

# Max. length of a word name
WORD_NAME_LENGTH = 4

EMPTY_WORD = [0] * WORD_LENGTH

def word_cleanup(word):
    return ''.join([chr(x) for x in word if x != 0]).ljust(WORD_NAME_LENGTH)

class Word(object):
    def __init__(self, song, index):
        self.song = song
        self.index = index

        self.notes = self.song.song_data.words[index]

add_song_data_property(Word, "name", ("word_names",), use_index = True)

class SpeechInstrument(object):
    def __init__(self, song):
        self.song = song

        self.words = self.song.song_data.words
