from utils import add_song_data_property

class Synth(object):
    """The wave channel can be used as a soft synthesizer to generate sounds."""
    def __init__(self, song, index):
        self._params = song.song_data.softsynth_params[index]
        self.index = index

    def __getattr__(self, name):
        if name in ("_params", "index"):
            return super(Synth, self).__getattr__(name)
        else:
            return getattr(self._params, name)

    def __setattr__(self, name, value):
        if name in ("_params", "index"):
            super(Synth, self).__setattr__(name, value)
        else:
            setattr(self._params, name, value)
