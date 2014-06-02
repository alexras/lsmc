import os
import warnings
import sys
from struct import pack, unpack

def printable_decimal_and_hex(num):
    return "{0:d} (0x{0:x})".format(num)

def add_song_data_property(clazz, property_name, song_data_field_path,
                           use_index=False):
    """Add a property to the class `clazz` named `property_name`. This
    property's getter will return the field in self.song.song_data
    corresponding to `song_data_field_path`, and its setter will set that
    field. `song_data_field_path` is a tuple consisting of a sequence of field
    lookups that will lead to the desired field.
    """

    def get_field(self):
        field_val = self.song.song_data

        for field_name in song_data_field_path:
            field_val = getattr(field_val, field_name)

        if use_index:
            return field_val[self.index]
        else:
            return field_val

    def set_field(self, field_val):
        data_obj = self.song.song_data

        for field_name in song_data_field_path[:-1]:
            data_obj = getattr(data_obj, field_name)

        if use_index:
            getattr(data_obj, song_data_field_path[-1])[self.index] = field_val
        else:
            setattr(data_obj, song_data_field_path[-1], field_val)

    setattr(clazz, property_name, property(fset=set_field, fget=get_field))

def assert_index_sane(index, upper_bound_exclusive):
    assert type(index) == int, "Indices should be integers; '%s' is not" % (
        index)
    assert 0 <= index < upper_bound_exclusive, (
        "Index %d out of range [%d, %d)" % (index, 0, upper_bound_exclusive))

class ObjectLookupDict(object):
    def __init__(self, id_list, object_list):
        self.id_list = id_list
        self.object_list = object_list

    def __getitem__(self, index):
        assert_index_sane(index, len(self.id_list))

        return self.object_list[self.id_list[index]]

    def __setitem__(self, index, value):
        assert_index_sane(index, len(self.id_list))

        self.id_list[index] = value.index

def name_without_zeroes(name):
    """
    Return a human-readable name without LSDJ's trailing zeroes.
    """
    first_zero = name.find('\0')

    if first_zero == -1:
        return name
    else:
        return str(name[:first_zero])
