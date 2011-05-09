import filepack
import blocks
import instrument
import wave
import consts

# Maximum size of a block
BLOCK_SIZE = 0x200

class Block(object):
    def __init__(self, block_id, data):
        self.id = block_id
        self.data = data

    def __repr__(self):
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
        segments = filepack.split(compressed_data, blocks.BLOCK_SIZE)

        block_ids = []

        for segment in segments:
            block = factory.new_block()
            block_ids.append(block.id)

        for i in xrange(len(segments)):
            segment = segments[i]
            block = factory.blocks[block_ids[i]]

            assert len(block.data) == 0, "Encountered a block with "
            "pre-existing data while writing"

            if i == len(segments) - 1:
                # Write EOF to the end of the segment
                filepack.add_eof(segment)
            else:
                # Write a pointer to the next segment
                filepack.add_block_switch(segment, block_ids[i + 1])

            # Pad segment with zeroes until it's large enough
            filepack.pad(segment, blocks.BLOCK_SIZE)

            block.data = segment

        return block_ids

class BlockReader(object):

    def read(self, block_dict):
        """
        Parses a dictionary of blocks into a compressed byte stream
        """

        segment_dict = {}

        for (block_id, block) in block_dict.items():
            segment_dict[block_id] = block.data

        return filepack.merge(segment_dict)
