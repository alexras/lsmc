import json, os, sys, math, cProfile
from nose.tools import assert_equal, assert_less

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.join(SCRIPT_DIR, os.path.pardir))

import common.filepack as filepack
from common.project import Project

def test_read_write_project():
    sample_song_compressed = os.path.join(
        SCRIPT_DIR, "test_data", "sample_song_compressed.json")

    with open(sample_song_compressed, "r") as fp:
        song_data_compressed = json.load(fp)

    song_data = filepack.decompress(song_data_compressed)
    song_name = "UNTOLDST"
    song_version = 23

    proj = Project(song_name, song_version, song_data)
    empty_instruments = [
        i for i in xrange(len(proj.song.instruments.alloc_table))
        if proj.song.instruments.alloc_table[i] == 0]

    assert_equal(proj.name, song_name)
    assert_equal(proj.version, song_version)

    raw_data = proj.get_raw_data()

    recompressed = filepack.compress(raw_data)

    assert_less(math.fabs(len(recompressed) - len(song_data_compressed)), 512)

    # Do comparison based on parsed object, since the actual input data can
    # contain noise
    proj_from_raw_data = Project(song_name, song_version, raw_data)

    assert_equal(proj_from_raw_data._song_data, proj._song_data)

if __name__ == "__main__":
    test_read_write_project()
