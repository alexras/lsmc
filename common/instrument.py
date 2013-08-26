from utils import assert_index_sane

class Instrument(object):
    def __init__(self, song, index):
        self.song = song
        self.data = song.song_data.instruments[index]
        self.index = index

        if hasattr(self.data, "table_on") and self.data.table_on:
            assert_index_sane(self.data.table, len(self.song.tables))
            self.table = self.song.tables[self.data.table]

    @property
    def name(self):
        return self.song.song_data.instrument_names[self.index]

    def __getattr__(self, name):
        if name == "wave":
            return self.song.song_data.wave_frames[self.index]
        else:
            return getattr(self.data, name)

    def __setattr__(self, name, value):
        if name == "name":
            self.song.song_data.instrument_names[self.index] = value
        else:
            setattr(self.data, name, value)
