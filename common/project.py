import sys
import bread
import bread_spec as spec
from song import Song

class Project(object):
    def __init__(self, name, version, data):
        self.name = name
        self.version = version

        self._song_data = bread.parse(data, spec.song)

        self.song = Song(self._song_data)

    def get_raw_data(self):
        return bread.write(self._song_data, spec.song)
