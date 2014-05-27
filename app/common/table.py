from utils import add_song_data_property

class Table(object):
    """Each table is a sequence of transposes, commands, and amplitude
    changes that can be applied to any channel."""
    def __init__(self, song, index):
        self.song = song
        self.index = index

for property_name, field_path in [
        ("envelopes", ("table_envelopes",)),
        ("transposes", ("table_transposes",)),
        ("fx1", ("table_cmd1", "fx")),
        ("fx1_vals", ("table_cmd1", "val")),
        ("fx2", ("table_cmd2", "fx")),
        ("fx2_vals", ("table_cmd2", "val"))]:
    add_song_data_property(Table, property_name, field_path, use_index=True)
