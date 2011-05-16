import os, sys

sys.path.append(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.path.pardir))))

import unittest
import common.blocks as bl
import common.filepack as filepack

class TestBlocks(unittest.TestCase):
    def test_simple_read_write(self):
        data = [i % 10 for i in xrange(bl.BLOCK_SIZE * 5 + 17)]

        reader = bl.BlockReader()
        writer = bl.BlockWriter()
        factory = bl.BlockFactory()

        block_ids = writer.write(data, factory)

        blocks = {}

        for i in block_ids:
            blocks[i] = factory.blocks[i]

        recovered_data = reader.read(blocks)

        self.assertEqual(data, recovered_data)

if __name__ == "__main__":
    unittest.main()


