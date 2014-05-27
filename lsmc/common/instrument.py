from utils import assert_index_sane
import json

import bread
import bread_spec

from filepack import DEFAULT_INSTRUMENT

def new_default_instrument(instr_type):
    instr_data = DEFAULT_INSTRUMENT[:]

    instr_name_to_code = {
        "pulse": 0,
        "wave": 1,
        "kit": 2,
        "noise": 3
    }

    instr_data[0] = instr_name_to_code[instr_type]

    return bread.parse(instr_data, bread_spec.instrument)

class Instrument(object):
    def __init__(self, song, index):
        self.song = song
        self.data = song.song_data.instruments[index]
        self.index = index

    @property
    def name(self):
        return self.song.song_data.instrument_names[self.index]

    @name.setter
    def name(self, val):
        self.song.song_data.instrument_names[self.index] = val

    @property
    def type(self):
        return self.data.instrument_type

    @type.setter
    def type(self, val):
        self.data.instrument_type = val

    def __getattr__(self, name):
        if name == "wave" and type == "wave":
            return self.song.song_data.wave_frames[self.index]
        elif name == "table":
            if hasattr(self.data, "table_on") and self.data.table_on:
                assert_index_sane(self.data.table, len(self.song.tables))
                return self.song.tables[self.data.table]
        elif name == "name":
            return self.song.song_data.instrument_names[self.index]
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

    def import_lsdinst(self, lsdinst_struct):
        self.name = lsdinst_struct["name"]

        # If this instrument is of a different type than we're currently
        # storing, we've got to make a new one of the appropriate type into
        # which to demarshal
        instr_type = lsdinst_struct["data"]["instrument_type"]

        if self.type != instr_type:
            self.data = new_default_instrument(instr_type)
            self.song.song_data.instruments[self.index] = self.data

        native_repr = self.data.as_native()
        self._import_instr_data(lsdinst_struct["data"], native_repr, self.data)

    def _import_instr_data(self, import_data, native_repr, output_data):
        for (key, val) in native_repr.items():
            if key[0] == '_':
                continue

            if type(val) == dict:
                self._import_instr_data(
                    import_data[key], val, getattr(output_data, key))
            else:
                setattr(output_data, key, import_data[key])

    def export(self):
        export_struct = {}

        export_struct["name"] = self.name
        export_struct["data"] = {}

        data_json = json.loads(self.data.as_json())

        for key, value in data_json.items():
            if key[0] != '_':
                export_struct["data"][key] = value

        return export_struct
