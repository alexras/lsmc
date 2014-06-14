import json
from utils import add_song_data_property
from bread_spec import STEPS_PER_TABLE

class Table(object):
    """Each table is a sequence of transposes, commands, and amplitude
    changes that can be applied to any channel."""
    def __init__(self, song, index):
        self.song = song
        self.index = index

    def export(self):
        export_struct = []

        for i in xrange(STEPS_PER_TABLE):
            export_struct.append({
                "volume": self.envelopes[i],
                "transpose": self.transposes[i],
                "cmd1": [self.fx1[i], self.fx1_vals[i]],
                "cmd2": [self.fx2[i], self.fx2_vals[i]]
            })

        return export_struct

    def import_lsdinst(self, table_data):
        for i, table_row in enumerate(table_data):
            self.envelopes[i] = table_row["volume"]
            self.transposes[i] = table_row["transpose"]
            self.fx1[i], self.fx1_vals[i] = table_row["cmd1"]
            self.fx2[i], self.fx2_vals[i] = table_row["cmd2"]


for property_name, field_path in [
        ("envelopes", ("table_envelopes",)),
        ("transposes", ("table_transposes",)),
        ("fx1", ("table_cmd1", "fx")),
        ("fx1_vals", ("table_cmd1", "val")),
        ("fx2", ("table_cmd2", "fx")),
        ("fx2_vals", ("table_cmd2", "val"))]:
    add_song_data_property(Table, property_name, field_path, use_index=True)
