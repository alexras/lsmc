from utils import ObjectLookupDict

class Chain(object):
    """A chain is a sequence of phrases for a single channel. Each phrase can be
    transposed by a number of semitones.
    """
    def __init__(self, song, index):
        self.song = song
        self.index = index

        self.transposes = self.song.song_data.chain_transposes[index]
        self.phrases = ObjectLookupDict(
            self.song.song_data.chain_phrases[index], self.song.phrases)
