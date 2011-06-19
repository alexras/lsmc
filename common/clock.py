from rich_comparable_mixin import RichComparableMixin

class Clock(RichComparableMixin):
    def __init__(self):
        self.days = 0
        self.hours = 0
        self.minutes = 0

    def __repr__(self):
        return "%d days, %d hours, %d minutes" % \
            (self.days, self.hours, self.minutes)

    @property
    def checksum(self):
        return self.days + self.hours + self.minutes
