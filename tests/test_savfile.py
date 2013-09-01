import os,sys
import unittest

sys.path.append(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.path.pardir))))

import common.savfile as savfile
from common.project import Project

class ProjectTests(unittest.TestCase):
    SAV_IN = os.path.join(os.path.dirname(__file__), "test_data", "lsdj.sav")
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

        print "Saving..."
        sav.save(ProjectTests.SAV_OUT)

        new_sav = savfile.SAVFile(ProjectTests.SAV_OUT)

        self.assertEqual(sav, new_sav)

if __name__ == "__main__":
    unittest.main()
