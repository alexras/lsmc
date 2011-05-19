#!/usr/bin/env python

from common.savfile import SAVFile
from common import utils
import tempfile

from optparse import OptionParser
import os, sys

def sav_split(filename, output_directory):
    sav = SAVFile(filename)

    for project in sav.projects:
        project_dir = str(os.path.join(output_directory, project.name))
        os.makedirs(project_dir)

        for (instr_index, instr) in enumerate(project.instruments):
            if not instr.allocated:
                continue

            if instr.name == None:
                instrument_name = "NONAME"
            else:
                instrument_name = instr.name

            instrument_name = "%02X_%s" % (instr_index, instrument_name)

            instr_file = utils.make_unique_filename(prefix=instrument_name,
                                                    suffix=".json",
                                                    parent=project_dir)
            instr.dump(instr_file)


def main():
    option_parser = OptionParser(usage="Usage: %prog [options] "
                                 "<LSDj .sav file> <output directory>")

    (options, args) = option_parser.parse_args()

    if len(args) != 2:
        option_parser.error("Incorrect argument count")

    (filename, output_directory) = args

    if not os.path.exists(filename):
        sys.exit("Can't find file '%s'" % (filename))

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    sav_split(filename, output_directory)

if __name__ == "__main__":
    main()
