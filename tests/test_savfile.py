import os,sys
from nose.tools import assert_equal, with_setup

sys.path.append(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.path.pardir))))

import lsmc.common.savfile as savfile
from lsmc.common.project import Project

SAV_IN = os.path.join(os.path.dirname(__file__), "test_data", "lsdj.sav")
SAV_OUT = os.path.join(os.path.dirname(__file__), "lsdj.sav.out")

def setup():
   if os.path.exists(SAV_OUT):
       os.unlink(SAV_OUT)

def teardown():
   if os.path.exists(SAV_OUT):
       os.unlink(SAV_OUT)

@with_setup(setup, teardown)
def test_project_save_load():
    print "Loading..."
    sav = savfile.SAVFile(SAV_IN)

    print "Saving..."
    sav.save(SAV_OUT)

    new_sav = savfile.SAVFile(SAV_OUT)

    assert_equal(sav, new_sav)
