import sys
import bread
import bread_spec as spec
from song import Song
import StringIO
import utils
import filepack
from blockutils import BlockWriter, BlockFactory

class Project(object):
    def __init__(self, name, version, size_blks, data):
        self.name = name
        self.version = version

        self._song_data = bread.parse(data, spec.song)

        self.song = Song(self._song_data)
        self.size_blks = size_blks

    def get_raw_data(self):
        return bread.write(self._song_data, spec.song)

    def save(self, filename):
        with open(filename, 'wb') as fp:
            writer = BlockWriter()
            factory = BlockFactory()

            preamble_data = bread.write(self, spec.lsdsng_preamble)
            raw_data = self.get_raw_data()
            compressed_data = filepack.compress(raw_data)

            writer.write(compressed_data, factory)

            fp.write(preamble_data)

            for key in sorted(factory.blocks.keys()):
                fp.write(bytearray(factory.blocks[key].data))

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
