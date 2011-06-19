from rich_comparable_mixin import RichComparableMixin

class Table(RichComparableMixin):
    def __init__(self):
        self.allocated = False
        self.transposes = []
        self.fx = []
        self.fx_vals = []
        self.fx2 = []
        self.fx2_vals = []

    def as_dict(self):
        write_dict = {}

        for key, value in self.__dict__.items():
            write_dict[key] = getattr(self, key)

        return write_dict

    def load(self, jsonObj):
        for key in self.__dict__:
            setattr(self, key, jsonObj[key])
