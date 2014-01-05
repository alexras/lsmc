import filepack
import instrument
import wave
import consts

"""LSDJ stores its data in a block-oriented format. This file contains a Block
object that encapsulates a block's data, and
"""

# Maximum size of a block - 512 bytes
BLOCK_SIZE = 0x200

class Block(object):
    def __init__(self, block_id, data):
        self.id = block_id
        self.data = data

    def __repr__(self): # pragma: no cover
        repr_str = "{"
        repr_str += "BLOCK %d (%d bytes)\n" % (self.id, len(self.data))

        i = 0

        while i < len(self.data):
            repr_str += '\t'.join(
                ["0x%02x" % (x) for x in
                 self.data[i:min(i + 10, len(self.data))]]) + "\n"

            i += 10

        repr_str += "}"
        return repr_str

class BlockFactory(object):
    """Each block's ID should correspond to its position in an array of blocks.
    """
    def __init__(self):
        self.max_id = 0
        self.blocks = {}

    def new_block(self):
        block = Block(self.max_id, [])
        self.blocks[self.max_id] = block
        self.max_id += 1

        return block

class BlockWriter(object):
    def write(self, compressed_data, factory):
        """Splits a compressed byte stream into blocks.
        """
        return filepack.split(compressed_data, BLOCK_SIZE,
                              factory)

class BlockReader(object):
    def read(self, block_dict):
        """Parses a dictionary of blocks into a compressed byte stream.
        """

        return filepack.merge(block_dict)
