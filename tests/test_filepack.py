import os, sys

sys.path.append(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.path.pardir))))

import unittest
import common.filepack as filepack
import common.instrument as instrument
import common.blockutils as bl
import common.wave as wave

class FilePackTest(unittest.TestCase):
    def test_basic_compress_decompress(self):
        data = [i % 10 for i in xrange(5000)]

        compressed = filepack.compress(data)

        decompressed = filepack.decompress(compressed)

        self.assertEqual(data, decompressed)

    def test_rle_compress(self):
        data = [0xde for i in xrange(150)]
        data.extend([0xfe for i in xrange(220)])
        data.append(42)
        data.append(17)

        compressed = filepack.compress(data)

        reference = [filepack.RLE_BYTE, 0xde, 150,
                     filepack.RLE_BYTE, 0xfe, 220,
                     42, 17]

        self.assertEqual(compressed, reference)

        decompressed = filepack.decompress(compressed)

        self.assertEqual(decompressed, data)

    def test_short_rle_compress(self):
        data = [0xde, 0xde, 42, 17, 12]

        compressed = filepack.compress(data)

        self.assertEqual(compressed, data)


    def test_rle_special_byte(self):
        data = [filepack.RLE_BYTE, filepack.RLE_BYTE,
                filepack.SPECIAL_BYTE, filepack.SPECIAL_BYTE,
                filepack.RLE_BYTE, filepack.SPECIAL_BYTE]

        reference = [filepack.RLE_BYTE, filepack.RLE_BYTE, filepack.RLE_BYTE,
                     filepack.RLE_BYTE, filepack.RLE_BYTE,
                     filepack.SPECIAL_BYTE, 2, filepack.RLE_BYTE,
                     filepack.RLE_BYTE, filepack.SPECIAL_BYTE,
                     filepack.SPECIAL_BYTE]

        compressed = filepack.compress(data)

        self.assertEqual(compressed, reference)

        decompressed = filepack.decompress(compressed)

        self.assertEqual(decompressed, data)

    def test_default_instr_compress(self):
        data = []

        for i in xrange(42):
            data.extend(instrument.DEFAULT)

        compressed = filepack.compress(data)
        reference = [filepack.SPECIAL_BYTE, filepack.DEFAULT_INSTR_BYTE, 42]

        self.assertEqual(compressed, reference)

        decompressed = filepack.decompress(compressed)

        self.assertEqual(data, decompressed)

    def test_default_wave_compress(self):
        data = []

        for i in xrange(33):
            data.extend(wave.DEFAULT)

        compressed = filepack.compress(data)
        reference = [filepack.SPECIAL_BYTE, filepack.DEFAULT_WAVE_BYTE, 33]

        self.assertEqual(compressed, reference)

        decompressed = filepack.decompress(compressed)

        self.assertEqual(data, decompressed)

    def test_large_rle_compress(self):
        data = []

        for i in xrange(275):
            data.append(42)

        compressed = filepack.compress(data)

        reference = [filepack.RLE_BYTE, 42, 255, filepack.RLE_BYTE, 42, 20]

        self.assertEqual(compressed, reference)

        decompressed = filepack.decompress(compressed)

        self.assertEqual(data, decompressed)

    def test_large_default_instr_compress(self):
        data = []

        for i in xrange(300):
            data.extend(instrument.DEFAULT)

        compressed = filepack.compress(data)

        reference = [filepack.SPECIAL_BYTE, filepack.DEFAULT_INSTR_BYTE, 255,
                     filepack.SPECIAL_BYTE, filepack.DEFAULT_INSTR_BYTE, 45]

        self.assertEqual(compressed, reference)

        decompressed = filepack.decompress(compressed)

        self.assertEqual(data, decompressed)

    def test_large_default_wave_compress(self):
        data = []

        for i in xrange(300):
            data.extend(wave.DEFAULT)

        compressed = filepack.compress(data)

        reference = [filepack.SPECIAL_BYTE, filepack.DEFAULT_WAVE_BYTE, 255,
                     filepack.SPECIAL_BYTE, filepack.DEFAULT_WAVE_BYTE, 45]

        self.assertEqual(compressed, reference)

        decompressed = filepack.decompress(compressed)

        self.assertEqual(data, decompressed)


    def test_bad_rle_split(self):
        data = [filepack.RLE_BYTE]

        factory = bl.BlockFactory()

        self.assertRaises(AssertionError, filepack.split, data, bl.BLOCK_SIZE,
                          factory)

    def test_bad_special_byte_split(self):
        data = [filepack.SPECIAL_BYTE]

        factory = bl.BlockFactory()

        self.assertRaises(AssertionError, filepack.split, data, bl.BLOCK_SIZE,
                          factory)

    def test_block_jump_during_split_asserts(self):
        data = [filepack.SPECIAL_BYTE, 47]

        factory = bl.BlockFactory()

        self.assertRaises(AssertionError, filepack.split, data, bl.BLOCK_SIZE,
                          factory)

    def test_special_byte_on_block_boundary(self):
        data = [42, 17, filepack.SPECIAL_BYTE, filepack.SPECIAL_BYTE,
                100, 36]

        factory = bl.BlockFactory()

        filepack.split(data, 5, factory)

        self.assertEqual(len(factory.blocks), 3)
        self.assertEqual(factory.blocks[0].data,
                         [42, 17, filepack.SPECIAL_BYTE, 1, 0])
        self.assertEqual(factory.blocks[1].data,
                         [filepack.SPECIAL_BYTE, filepack.SPECIAL_BYTE, 100,
                          filepack.SPECIAL_BYTE, 2])
        self.assertEqual(factory.blocks[2].data,
                         [36, filepack.SPECIAL_BYTE, filepack.EOF_BYTE, 0, 0])

    def test_rle_byte_on_block_boundary(self):
        data = [42, 17, filepack.RLE_BYTE, filepack.RLE_BYTE,
                100, 36]

        factory = bl.BlockFactory()

        filepack.split(data, 5, factory)

        self.assertEqual(len(factory.blocks), 3)
        self.assertEqual(factory.blocks[0].data,
                         [42, 17, filepack.SPECIAL_BYTE, 1, 0])
        self.assertEqual(factory.blocks[1].data,
                         [filepack.RLE_BYTE, filepack.RLE_BYTE, 100,
                          filepack.SPECIAL_BYTE, 2])
        self.assertEqual(factory.blocks[2].data,
                         [36, filepack.SPECIAL_BYTE, filepack.EOF_BYTE, 0, 0])

    def test_full_rle_on_block_boundary(self):
        data = [42, filepack.RLE_BYTE, 55, 4, 22, 3]

        factory = bl.BlockFactory()

        filepack.split(data, 5, factory)

        self.assertEqual(len(factory.blocks), 3)
        self.assertEqual(factory.blocks[0].data,
                         [42, filepack.SPECIAL_BYTE, 1, 0, 0])
        self.assertEqual(factory.blocks[1].data,
                         [filepack.RLE_BYTE, 55, 4, filepack.SPECIAL_BYTE, 2])
        self.assertEqual(factory.blocks[2].data,
                         [22, 3, filepack.SPECIAL_BYTE, filepack.EOF_BYTE, 0])

    def test_default_on_block_boundary(self):
        data = [42, filepack.SPECIAL_BYTE, filepack.DEFAULT_INSTR_BYTE, 3, 2, 5]

        factory = bl.BlockFactory()

        filepack.split(data, 5, factory)

        self.assertEqual(len(factory.blocks), 3)
        self.assertEqual(factory.blocks[0].data,
                         [42, filepack.SPECIAL_BYTE, 1, 0, 0])
        self.assertEqual(factory.blocks[1].data,
                         [filepack.SPECIAL_BYTE, filepack.DEFAULT_INSTR_BYTE, 3,
                          filepack.SPECIAL_BYTE, 2])
        self.assertEqual(factory.blocks[2].data,
                         [2, 5, filepack.SPECIAL_BYTE, filepack.EOF_BYTE, 0])

    def test_merge_with_rle_byte(self):
        factory = bl.BlockFactory()

        block1 = factory.new_block()
        block1.data = [filepack.RLE_BYTE, filepack.RLE_BYTE, 2, 1, 3,
                       filepack.SPECIAL_BYTE, 1, 0, 0]
        block2 = factory.new_block()
        block2.data = [4, 3, 6, filepack.SPECIAL_BYTE, filepack.EOF_BYTE]

        data = filepack.merge(factory.blocks)

        self.assertEqual(data, [filepack.RLE_BYTE, filepack.RLE_BYTE, 2, 1, 3,
                                4, 3, 6])

    def test_merge_with_full_rle(self):
        factory = bl.BlockFactory()
        block1 = factory.new_block()
        block1.data = [filepack.RLE_BYTE, 42, 17, 1, 1, 4,
                       filepack.SPECIAL_BYTE, 1, 0, 0]
        block2 = factory.new_block()
        block2.data = [4, 4, 42, filepack.SPECIAL_BYTE, filepack.EOF_BYTE]

        data = filepack.merge(factory.blocks)

        self.assertEqual(data, [filepack.RLE_BYTE, 42, 17, 1, 1, 4, 4, 4, 42])

    def test_merge_with_special_byte(self):
        factory = bl.BlockFactory()

        block1 = factory.new_block()
        block1.data = [filepack.SPECIAL_BYTE, filepack.SPECIAL_BYTE, 2, 1, 3,
                       filepack.SPECIAL_BYTE, 1, 0, 0]
        block2 = factory.new_block()
        block2.data = [4, 3, 6, filepack.SPECIAL_BYTE, filepack.EOF_BYTE]

        data = filepack.merge(factory.blocks)

        self.assertEqual(data, [filepack.SPECIAL_BYTE, filepack.SPECIAL_BYTE,
                                2, 1, 3, 4, 3, 6])


    def test_merge_with_special_command(self):
        factory = bl.BlockFactory()

        block1 = factory.new_block()
        block1.data = [filepack.SPECIAL_BYTE, filepack.DEFAULT_INSTR_BYTE, 4, 6,
                       1, 93, filepack.SPECIAL_BYTE, 1, 0, 0]
        block2 = factory.new_block()
        block2.data = [3, 3, 33, filepack.SPECIAL_BYTE, filepack.EOF_BYTE]

        data = filepack.merge(factory.blocks)

        self.assertEquals(data, [filepack.SPECIAL_BYTE,
                                 filepack.DEFAULT_INSTR_BYTE, 4, 6,
                                 1, 93, 3, 3, 33])

    def test_decompress_bogus_special_byte_asserts(self):
        data = [filepack.SPECIAL_BYTE, filepack.EOF_BYTE]

        self.assertRaises(AssertionError, filepack.decompress, data)



if __name__ == "__main__":
    unittest.main()
