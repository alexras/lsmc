import sys, math
import bread
import bread_spec as spec
from song import Song
import StringIO
import utils
import filepack
import blockutils
from blockutils import BlockReader, BlockWriter, BlockFactory

def load_project(filename):
    # Load preamble data so that we know the name and version of the song
    with open(filename, 'rb') as fp:
        preamble_data = bread.parse(fp, spec.lsdsng_preamble)

    with open(filename, 'rb') as fp:
        # Skip the preamble this time around
        fp.seek(len(preamble_data) / 8)

        # Load compressed data into a block map and use BlockReader to
        # decompress it
        factory = BlockFactory()

        while True:
            block_data = bytearray(fp.read(blockutils.BLOCK_SIZE))

            if len(block_data) == 0:
                break

            block = factory.new_block()
            block.data = block_data

        remapped_blocks = filepack.renumber_block_keys(factory.blocks)

        reader =  BlockReader()
        compressed_data = reader.read(remapped_blocks)

        # Now, decompress the raw data and use it and the preamble to construct
        # a Project
        raw_data = filepack.decompress(compressed_data)

        name = preamble_data.name
        version = preamble_data.version
        size_blks = int(math.ceil(
            float(len(compressed_data)) / blockutils.BLOCK_SIZE))

        return Project(name, version, size_blks, raw_data)

class Project(object):
    def __init__(self, name, version, size_blks, data):
        self.name = name
        self.version = version

        self._song_data = bread.parse(data, spec.song)

        self.song = Song(self._song_data)
        self.size_blks = size_blks

        # Useful for applications tracking whether a project was modified since
        # it was loaded.
        self.modified = False

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
        print >>out_str, "<%s, %d>" % (self.name, self.version)

        string = out_str.getvalue()
        out_str.close()
        return string
