from rich_comparable_mixin import RichComparableMixin

class Clock(RichComparableMixin):
    """LSDJ has a couple of clocks (the current session time, and the total
    session time). Each clock has a checksum, which is one more way of making
    sure battery RAM isn't corrupted."""
    def __init__(self, days, hours, minutes, checksum):
        assert checksum == days + hours + minutes

        self.days = days
        self.hours = hours
        self.minutes = minutes

    def __repr__(self):
        return "%d days, %d hours, %d minutes" % \
            (self.days, self.hours, self.minutes)
