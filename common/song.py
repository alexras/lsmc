from rich_comparable_mixin import RichComparableMixin

# Number of channels
NUM_CHANNELS = 4

class Song(RichComparableMixin):
    """A song consists of a sequence of chains, one per channel.
    """
    def __init__(self, chains):
        self.chains = chains
