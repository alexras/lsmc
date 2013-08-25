from rich_comparable_mixin import RichComparableMixin

class Clock(RichComparableMixin):
    """LSDJ has a couple of clocks (the current session time, and the total
    session time). Each clock has a checksum, which is one more way of making
    sure battery RAM isn't corrupted."""
    def __init__(self, clock_data):
        assert (clock_data.checksum ==
                clock_data.days + clock_data.hours + clock_data.minutes)
        self._clock_data = clock_data

    def _update_checksum(self):
        self._clock_data.checksum = (
            self._clock_data.days
            + self._clock_data.hours
            + self._clock_data.minutes)

    @property
    def days(self):
        return self._clock_data.days

    @days.setter
    def days(self, days):
        self._clock_data.days = days
        self._update_checksum()

    @property
    def hours(self):
        return self._clock_data.hours

    @hours.setter
    def hours(self, hours):
        self._clock_data.hours = hours
        self._update_checksum()

    @property
    def minutes(self):
        return self._clock_data.minutes

    @minutes.setter
    def minutes(self, minutes):
        self._clock_data.minutes = minutes
        self._update_checksum()

    def __repr__(self):
        return "%d days, %d hours, %d minutes" % \
            (self.days, self.hours, self.minutes)
