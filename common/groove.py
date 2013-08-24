from rich_comparable_mixin import RichComparableMixin

class Groove(RichComparableMixin):
    """Grooves define the way that phrases and tables are played back to give
    songs a little extra swing. It does this by changing the number of ticks a
    note should take to play back. The length of a tick varies based on the
    tempo, but is usually around 1/60th of a second."""
    def __init__(self):
        self.ticks = []
