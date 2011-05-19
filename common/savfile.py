import os
import sys
from struct import unpack
import utils
from StringIO import StringIO
from project import Project
import blockutils
from blockutils import BlockReader, BlockWriter, BlockFactory
import filepack

class SAVFile(object):
    # Start offset of SAV file contents
    START_OFFSET = 0x8000

    HEADER_EMPTY_SECTION_1 = (0x8120, 0x813d)

    # Offset of SRAM initialization check
    SRAM_INIT_CHECK_OFFSET = 0x813e
    SRAM_INIT_CHECK_LENGTH = 2

    # Offset where active file number appears
    ACTIVE_FILE_NUMBER_OFFSET = 0x8140

    # Start of block allocation table
    BAT_START_OFFSET = 0x8141

    # End of block allocation table
    BAT_END_OFFSET = 0x81ff

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

    def __init__(self, filename):
        self.projects = []

        fp = open(filename, 'r')

        self.preamble = fp.read(self.START_OFFSET)

        filenames = []

        for i in xrange(self.NUM_FILES):
            filenames.append(fp.read(self.FILENAME_LENGTH))

        file_versions = []

        for i in xrange(self.NUM_FILES):
            file_versions.append(utils.binary_read_uint(
                    fp, self.FILE_VERSION_LENGTH))

        fp.seek(self.SRAM_INIT_CHECK_OFFSET, os.SEEK_SET)

        sram_check = fp.read(self.SRAM_INIT_CHECK_LENGTH)

        if sram_check != 'jk':
            assert False, "SRAM init check bits incorrect " \
                "(should be 'jk', was '%s')" % (sram_check)

        self.active_project_number = utils.binary_read_uint(
            fp, self.FILE_NUMBER_LENGTH)

        file_blocks = {}

        for i in xrange(self.BAT_START_OFFSET, self.BAT_END_OFFSET + 1):
            block_number = i - self.BAT_START_OFFSET + 1
            file_number = utils.binary_read_uint(fp, self.FILE_NUMBER_LENGTH)

            if file_number != self.EMPTY_BLOCK:
                if file_number not in file_blocks:
                    file_blocks[file_number] = []

                file_blocks[file_number].append(block_number)

        for file_number in file_blocks:
            block_numbers = file_blocks[file_number]
            block_map = {}

            for block_number in block_numbers:
                offset = self.BLOCKS_START_OFFSET + \
                    (block_number * blockutils.BLOCK_SIZE)

                fp.seek(offset, os.SEEK_SET)

                block_contents = fp.read(blockutils.BLOCK_SIZE)

                block_data = utils.binary_uint(
                    block_contents, 1, len(block_contents))

                block_map[block_number] = blockutils.Block(block_number,
                                                           block_data)

            project = Project(name = filenames[file_number],
                              version = file_versions[file_number])

            reader = BlockReader()

            compressed_data = reader.read(block_map)

            raw_data = filepack.decompress(compressed_data)

            project.load_data(raw_data)

            self.projects.append(project)

        fp.close()

    def __str__(self):

        str_stream = StringIO()

        for project in self.projects:
            print >>str_stream, str(project)

        print >>str_stream, "Active Project: %s" % \
            (self.projects[self.active_project_number])

        str_stream_stringval = str_stream.getvalue()
        str_stream.close()
        return str_stream_stringval

    def save(self, filename):
        fp = open(filename, 'w')

        writer = BlockWriter()
        factory = BlockFactory()

        # Block allocation table doesn't include header block because it's
        # always in use, so have to add additional block to account for header
        num_blocks = self.BAT_END_OFFSET - self.BAT_START_OFFSET + 2

        header_block = factory.new_block()

        block_table = []

        for i in xrange(num_blocks):
            block_table.append(None)

        # First block is the header block, so we should ignore it when creating
        # the block allocation table
        block_table[0] = -1

        for (i, project) in enumerate(self.projects):
            raw_data = project.get_raw_data()

            compressed_data = filepack.compress(raw_data)

            project_block_ids = writer.write(compressed_data, factory)

            for b in project_block_ids:
                block_table[b] = i

        # Bytes up to START_OFFSET will remain the same
        fp.write(self.preamble)

        for project in self.projects:
            name_bytes = utils.string_to_bytes(project.name,
                                               self.FILENAME_LENGTH)

            header_block.data.extend(name_bytes)

        empty_project_name = []

        for i in xrange(self.FILENAME_LENGTH):
            empty_project_name.append(0)

        for i in xrange(self.NUM_FILES - len(self.projects)):
            header_block.data.extend(empty_project_name)

        for project in self.projects:
            header_block.data.append(project.version)

        for i in xrange(self.NUM_FILES - len(self.projects)):
            header_block.data.append(0)

        for i in xrange(self.HEADER_EMPTY_SECTION_1[0],
                        self.HEADER_EMPTY_SECTION_1[1] + 1):
            header_block.data.append(0)

        header_block.data.extend([ord('j'), ord('k')])

        header_block.data.append(self.active_project_number)

        # Ignore the header block when serializing the block allocation table
        for b in block_table[1:]:
            if b == None:
                file_no = self.EMPTY_BLOCK
            else:
                file_no = b
            header_block.data.append(file_no)

        assert len(header_block.data) == blockutils.BLOCK_SIZE, \
            "Header block isn't the expected length; expected 0x%x, got 0x%x" \
            % (blockutils.BLOCK_SIZE, len(header_block.data))

        block_map = factory.blocks

        empty_block_data = []
        for i in xrange(blockutils.BLOCK_SIZE):
            empty_block_data.append(0)

        for i in xrange(num_blocks):
            if i in block_map:
                data_list = block_map[i].data
            else:
                data_list = empty_block_data

            utils.binary_write_uint_list(fp, data_list, 1)

        fp.close()

if __name__ == "__main__":
    sav = SAVFile(sys.argv[1])
    sav.save(sys.argv[2])
