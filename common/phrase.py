class Phrase(object):
    def __init__(self):
        self.notes = []

    def __repr__(self):
        if sum(self.notes) == 0:
            return "Empty phrase"
        else:
            return repr(self.notes)
