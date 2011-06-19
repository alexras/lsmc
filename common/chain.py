from rich_comparable_mixin import RichComparableMixin

class Chain(RichComparableMixin):
    def __init__(self):
        self.phrases = []
        self.transposes = []
