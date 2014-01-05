from utils import add_song_data_property, assert_index_sane, ObjectLookupDict

class Phrase(object):
    """A phrase is a sequence of notes for a single channel.
    """
    def __init__(self, song, index):
        self.song = song
        self.index = index
        self.instruments = ObjectLookupDict(
            self.song.song_data.phrase_instruments[index],
            self.song.instruments)

for property_name in ["notes", "fx", "fx_val"]:
    add_song_data_property(Phrase, property_name, ("phrase_" + property_name,),
                           use_index = True)
