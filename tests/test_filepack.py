import os, sys

sys.path.append(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.path.pardir))))

import unittest
import common.filepack as filepack
import common.instrument as instrument
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

if __name__ == "__main__":
    unittest.main()
