import os,sys
import unittest

sys.path.append(os.path.dirname(
        os.path.abspath(os.path.join(__file__, os.path.pardir))))

from common.pulse_instrument import PulseInstrument

class PulseInstrumentTest(unittest.TestCase):
    def test_example_instrument(self):
        raw_data = [0, 136, 0, 0, 255, 0, 0, 3, 0, 0, 208, 0, 0, 0, 243, 0]

        instr = PulseInstrument()
        instr.params = raw_data

        self.assertEqual(instr.envelope, 0x88)
        self.assertEqual(instr.sweep, 0xff)
        self.assertEqual(instr.table_number, 0)
        self.assertEqual(0, instr.has_table)



if __name__ == "__main__":
    unittest.main()
