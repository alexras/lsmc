#!/usr/bin/env python

import os, sys
import utils
from optparse import OptionParser

def binary_dump(filename, offset, size, width, line_numbers):
    fp = open(filename)

    fp.seek(offset)

    data = utils.binary_read_uint_list(fp, 1, size)

    i = 0
    while i < len(data):
        if line_numbers:
            print "0x%04X: " % (i),
        print ' '.join("0x%02x" % (x) for x in data[i: i + width])
        i += width

    fp.close()

def main():
    optionParser = OptionParser(usage="usage: %prog [options] <filename>")

    optionParser.add_option("-s", "--size",
                            help="amount of data to dump in bytes "
                            "(defaults to whole file)", default=-1,
                            type=int)
    optionParser.add_option("-o", "--offset",
                            help="offset within file to start reading, "
                            "in bytes (default %default)", default=0, type=int)
    optionParser.add_option("-w", "--width", help="width of the dump output , "
                            "in bytes (default %default)", default=10, type=int)
    optionParser.add_option("-n", "--line_numbers", help="show line numbers",
                            default=False, action="store_true")

    (options, args) = optionParser.parse_args()

    if len(args) != 1:
        optionParser.error("Incorrect argument count")

    filename = args[0]

    if not os.path.exists(filename):
        sys.exit("Can't find file '%s'" % (filename))

    if options.size == -1:
        options.size = os.path.getsize(filename)

    binary_dump(filename = filename,
                offset = options.offset,
                size = options.size,
                width = options.width,
                line_numbers = options.line_numbers)

if __name__ == "__main__":
    main()
