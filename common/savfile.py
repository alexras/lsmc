import os
import sys
from struct import unpack
import utils
from StringIO import StringIO

from project import Project

class SAVFile(object):
    # Start offset of SAV file contents
    START_OFFSET = 0x8000

    # Offset where active file number appears
    ACTIVE_FILE_NUMBER_OFFSET = 0x8140

    # Start of block allocation table
    BAT_START_OFFSET = 0x8141

    # End of block allocation table
    BAT_END_OFFSET = 0x8200

    # Start index for data blocks
    # The file's header is block 0, so blocks are indexed from 1
    BLOCKS_START_OFFSET = 0x8000


    # The maximum number of files that the .sav can support
    NUM_FILES = 0x20

    # Max length in bytes of filename
    FILENAME_LENGTH = 8

    # Length in bytes of file version number
    FILE_VERSION_LENGTH = 1

    # Length in bytes of file number
    FILE_NUMBER_LENGTH = 1

    #Constants
    EMPTY_BLOCK = 0xff
    BLOCK_SIZE = 0x200

    def __init__(self):
        self.projects = []
        self.active_project_number = None

    def __str__(self):

        str_stream = StringIO()

        for project in self.projects:
            print >>str_stream, str(project)

        print >>str_stream, "Active Project: %s" % \
            (self.projects[self.active_project_number])

        str_stream_stringval = str_stream.getvalue()
        str_stream.close()
        return str_stream_stringval

    def load(self, filename):
        fp = open(filename, 'r')

        fp.seek(self.START_OFFSET)

        filenames = []

        for i in xrange(self.NUM_FILES):
            filenames.append(fp.read(self.FILENAME_LENGTH))

        file_versions = []

        for i in xrange(self.NUM_FILES):
            file_versions.append(utils.binary_read_uint(
                    fp, self.FILE_VERSION_LENGTH))

        fp.seek(self.ACTIVE_FILE_NUMBER_OFFSET, os.SEEK_SET)

        self.active_project_number = utils.binary_read_uint(
            fp, self.FILE_NUMBER_LENGTH)

        file_blocks = {}

        for i in xrange(self.BAT_START_OFFSET, self.BAT_END_OFFSET):
            block_number = i - self.BAT_START_OFFSET + 1
            file_number = utils.binary_read_uint(fp, self.FILE_NUMBER_LENGTH)

            if file_number != self.EMPTY_BLOCK:
                if file_number not in file_blocks:
                    file_blocks[file_number] = []

                file_blocks[file_number].append(block_number)

        for file_number in file_blocks:
            block_numbers = file_blocks[file_number]
            blocks = {}

            for block_number in block_numbers:
                offset = self.BLOCKS_START_OFFSET + \
                    (block_number * self.BLOCK_SIZE)
                fp.seek(offset, os.SEEK_SET)

                block_contents = fp.read(self.BLOCK_SIZE)
                blocks[block_number] = utils.binary_uint(
                    block_contents, 1, len(block_contents))

            project = Project(name = filenames[file_number],
                              version = file_versions[file_number],
                              blocks = blocks)
            self.projects.append(project)

        fp.close()


if __name__ == "__main__":
    sav = SAVFile()
    sav.load(sys.argv[1])
    print sav
