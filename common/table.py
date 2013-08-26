from utils import add_song_data_property

class Table(object):
    """Each table is a sequence of transposes, commands, and amplitude
    changes that can be applied to any channel."""
    def __init__(self, song, index):
        self.song = song
        self.index = index

for property_name in ["envelopes", "transposes", "fx", "fx_val", "fx2",
                      "fx2_val"]:
    add_song_data_property(Table, property_name, ("table_" + property_name,),
                           use_index=True)
