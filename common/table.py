from rich_comparable_mixin import RichComparableMixin

class Table(RichComparableMixin):
    """Each table is a sequence of transposes, commands, and amplitude
    changes that can be applied to any channel."""
    def __init__(self, transposes, fx, fx_vals, fx2, fx2_vals):
        self.transposes = transposes
        self.fx = fx
        self.fx_vals = fx_vals
        self.fx2 = fx2
        self.fx2_vals = fx2_vals

    def as_dict(self):
        write_dict = {}

        for key, value in self.__dict__.items():
            write_dict[key] = getattr(self, key)

        return write_dict

    def load(self, jsonObj):
        for key in self.__dict__:
            setattr(self, key, jsonObj[key])
