import os,sys
import unittest

sys.path.append(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.path.pardir))))

import common.savfile as savfile

class ProjectTests(unittest.TestCase):
    def setUp(self):
       if os.path.exists("lsdj.sav.out"):
           os.unlink("lsdj.sav.out")

    def tearDown(self):
       if os.path.exists("lsdj.sav.out"):
           os.unlink("lsdj.sav.out")

    def test_project_save_load(self):
        sav = savfile.SAVFile(os.path.join("test_data", "lsdj.sav"))

        sav.save("lsdj.sav.out")

        new_sav = savfile.SAVFile("lsdj.sav.out")

        self.assertEqual(sav, new_sav)

if __name__ == "__main__":
    unittest.main()
