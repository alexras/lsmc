from rich_comparable_mixin import RichComparableMixin
import json

class Phrase(RichComparableMixin):
    """A phrase is a sequence of notes for a single channel.
    """
    def __init__(self, notes, fx, fx_val, instruments):
        self.notes = notes
        self.fx = fx
        self.fx_val = fx_val
        self.instruments = instruments

    def __repr__(self):
        if sum(self.notes) == 0:
            return "Empty phrase"
        else:
            return repr(self.notes)

    def dump(self, filename):
        dump_dict = {}

        dump_dict["notes"] = self.notes

        fp = open(filename, 'w+')
        json.dump(dump_dict, fp)
        fp.close()
