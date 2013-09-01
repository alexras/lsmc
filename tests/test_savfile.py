import os,sys
import unittest

sys.path.append(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.path.pardir))))

import common.savfile as savfile
from common.project import Project

class ProjectTests(unittest.TestCase):
    SAV_IN = os.path.join(os.path.dirname(__file__), "test_data", "lsdj_2.sav")
    SAV_OUT = os.path.join(os.path.dirname(__file__), "lsdj.sav.out")

    def setUp(self):
       if os.path.exists(ProjectTests.SAV_OUT):
           os.unlink(ProjectTests.SAV_OUT)

    def tearDown(self):
        pass
       # if os.path.exists(ProjectTests.SAV_OUT):
       #     os.unlink(ProjectTests.SAV_OUT)

    def test_project_save_load(self):
        print "Loading..."
        sav = savfile.SAVFile(ProjectTests.SAV_IN)

        proj = sav.projects[0]

        for i in xrange(0x40):
            print proj.song.instruments[i]

        instr_0 = proj.song.instruments[0]
        assert instr_0.instrument_type == "pulse"
        assert instr_0.envelope == 0xa6

        instr_1 = proj.song.instruments[1]
        assert instr_1.instrument_type == "pulse"
        assert instr_1.envelope == 0xa8
        # assert instr_1.sound_length == 0x34

        instr_2 = proj.song.instruments[2]
        assert instr_2.instrument_type == "pulse"
        assert instr_2.pan == "L"

        instr_3 = proj.song.instruments[3]
        assert instr_3.instrument_type == "wave"
        assert instr_3.synth == 0
        assert instr_3.speed == 4

        instr_5 = proj.song.instruments[5]
        assert instr_5.instrument_type == "noise"
        assert instr_5.envelope == 0xa6

        instr_8 = proj.song.instruments[8]
        assert instr_8.envelope == 0xa8
        assert instr_8.sweep == 0xff

        print "Saving..."
        sav.save(ProjectTests.SAV_OUT)

        new_sav = savfile.SAVFile(ProjectTests.SAV_OUT)

        self.assertEqual(sav, new_sav)

if __name__ == "__main__":
    unittest.main()
