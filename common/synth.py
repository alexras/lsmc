from rich_comparable_mixin import RichComparableMixin

class Synth(RichComparableMixin):
    def __init__(self):
        self.params = []
        self.waves = []
