from rich_comparable_mixin import RichComparableMixin

# Number of channels
NUM_CHANNELS = 4

class Song(RichComparableMixin):
    def __init__(self):
        self.chain_numbers = []
