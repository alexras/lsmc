from utils import assert_index_sane

class Instrument(object):
    def __init__(self, song, index):
        self.song = song
        self.data = song.song_data.instruments[index]
        self.index = index

    @property
    def name(self):
        return self.song.song_data.instrument_names[self.index]

    def __getattr__(self, name):
        if name == "wave":
            return self.song.song_data.wave_frames[self.index]
        elif name == "table":
            if hasattr(self.data, "table_on") and self.data.table_on:
                assert_index_sane(self.data.table, len(self.song.tables))
                return self.song.tables[self.data.table]
        else:
            return getattr(self.__dict__["data"], name)

    def __setattr__(self, name, value):
        if name == "name":
            self.song.song_data.instrument_names[self.index] = value
        elif name in ["data", "song", "index"]:
            self.__dict__[name] = value
        elif name == "table":
            if not hasattr(self.data, "table_on"):
                raise ValueError("This instrument doesn't have a table")

            self.data.table_on = True
            self.data.table = value.index
        else:
            setattr(self.data, name, value)
