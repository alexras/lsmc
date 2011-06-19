from rich_comparable_mixin import RichComparableMixin

class Phrase(RichComparableMixin):
    def __init__(self):
        self.notes = []

    def __repr__(self):
        if sum(self.notes) == 0:
            return "Empty phrase"
        else:
            return repr(self.notes)
