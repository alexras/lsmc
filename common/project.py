import sys
import bread
import bread_spec as spec
from song import Song
import StringIO

class Project(object):
    def __init__(self, name, version, data):
        self.name = name
        self.version = version

        self._song_data = bread.parse(data, spec.song)

        self.song = Song(self._song_data)

    def get_raw_data(self):
        return bread.write(self._song_data, spec.song)

    def __eq__(self, other):
        return self._song_data == other._song_data

    def __str__(self):
        out_str = StringIO.StringIO()

        print >>out_str, "Project Name: ", self.name
        print >>out_str, "     Version: ", self.version
        print >>out_str, ""
        print >>out_str, str(self.song)

        string = out_str.getvalue()
        out_str.close()
        return string
