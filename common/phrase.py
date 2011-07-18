from rich_comparable_mixin import RichComparableMixin
import json

class Phrase(RichComparableMixin):
    def __init__(self):
        self.notes = []

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
