from rich_comparable_mixin import RichComparableMixin

class Chain(RichComparableMixin):
    """A chain is a sequence of phrases for a single channel. Each phrase can be
    transposed by a number of semitones.
    """
    def __init__(self, phrases, transposes):
        self.phrases = phrases
        self.transposes = transposes
