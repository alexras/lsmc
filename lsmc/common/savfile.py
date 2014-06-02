import bread_spec
import bread
import os
import sys
from struct import unpack
import utils
from StringIO import StringIO
from project import Project
import blockutils
from blockutils import BlockReader, BlockWriter, BlockFactory
import filepack
import collections
import bitstring

# By default, SAV file loading doesn't trigger any callback action
def _noop_callback(message, step, total_steps, continuing):
    pass

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

    def __init__(self, filename, callback=_noop_callback):
        with open(filename, 'rb') as fp:
            self._load(fp, callback)

    def _load(self, fp, callback):
        # 32 possible projects + read preamble + decompress blocks + "all done"
        total_steps = 35
        current_step = 0

        self.projects = {}

        callback("Reading preamble", current_step, total_steps, True)

        self.preamble = fp.read(self.START_OFFSET)

        header_block_data = fp.read(blockutils.BLOCK_SIZE)

        self.header_block = bread.parse(
            header_block_data, bread_spec.compressed_sav_file)

        if self.header_block.sram_init_check != 'jk':
            error_msg = (
                "SRAM init check bits incorrect (should be 'jk', was '%s')" %
                (self.header_block.sram_init_check))

            callback(error_msg, current_step, total_steps, False)
            raise ValueError(error_msg)

        self.active_project_number = self.header_block.active_file

        current_step += 1

        callback("Decompressing", current_step, total_steps, True)

        file_blocks = collections.defaultdict(list)

        for block_number, file_number in enumerate(
                self.header_block.block_alloc_table):
            if file_number == self.EMPTY_BLOCK:
                continue

            if file_number < 0 or file_number > 0x1f:
                callback(
                    "File number %x for block %x out of range" %
                    (file_number, block_number),
                    current_step, total_steps, False)

            # The file's header is block 0, so blocks are indexed from 1
            file_blocks[file_number].append(block_number + 1)

        current_step += 1

        for file_number in file_blocks:
            block_numbers = file_blocks[file_number]
            project_size_blks = len(block_numbers)

            block_map = {}

            for block_number in block_numbers:
                offset = self.BLOCKS_START_OFFSET + \
                    (block_number * blockutils.BLOCK_SIZE)

                fp.seek(offset, os.SEEK_SET)

                block_data = bytearray(fp.read(blockutils.BLOCK_SIZE))

                block_map[block_number] = blockutils.Block(block_number,
                                                           block_data)

            reader = BlockReader()
            compressed_data = reader.read(block_map)
            raw_data = filepack.decompress(compressed_data)

            project_name = self.header_block.filenames[file_number]
            project_version = self.header_block.file_versions[file_number]

            callback("Reading project '%s' v%d" %
                     (utils.name_without_zeroes(project_name), project_version),
                     current_step, total_steps, True)

            project = Project(
                name = self.header_block.filenames[file_number],
                version = self.header_block.file_versions[file_number],
                data = raw_data,
                size_blks = project_size_blks)

            self.projects[file_number] = project

            current_step += 1

        for i in xrange(self.NUM_FILES):
            if i not in self.projects:
                self.projects[i] = None

        callback("Import complete!", total_steps, total_steps, True)

    def __str__(self):

        str_stream = StringIO()

        for i, project in self.projects.items():
            if project is not None:
                print >>str_stream, str(project)

        print >>str_stream, "Active Project: %s" % \
            (self.projects[self.active_project_number])

        str_stream_stringval = str_stream.getvalue()
        str_stream.close()
        return str_stream_stringval

    def __eq__(self, other):
        return self.projects == other.projects

    @property
    def project_list(self):
        return [(i, self.projects[i]) for i in sorted(self.projects.keys())]

    def _save(self, fp, callback):
        # Marshal 32 possible projects + write preamble + write data + "all done"
        total_steps = 35
        current_step = 0

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

        for (i, project) in self.projects.items():
            current_step += 1

            if project is None:
                continue

            callback("Marshaling song '%s'" % (project.name),
                     current_step - 1, total_steps, True)

            raw_data = project.get_raw_data()
            compressed_data = filepack.compress(raw_data)

            project_block_ids = writer.write(compressed_data, factory)

            for b in project_block_ids:
                block_table[b] = i

        callback("Writing preamble and constructing header block",
                 current_step, total_steps, True)
        current_step += 1
        # Bytes up to START_OFFSET will remain the same
        fp.write(self.preamble)

        # Set header block filenames and versions

        empty_project_name = '\0' * self.FILENAME_LENGTH

        for i, project in self.projects.items():
            if project is None:
                self.header_block.filenames[i] = empty_project_name
                self.header_block.file_versions[i] = 0
            else:
                self.header_block.filenames[i] = project.name
                self.header_block.file_versions[i] = project.version

        self.header_block.active_file = self.active_project_number

        # Ignore the header block when serializing the block allocation table
        for i, b in enumerate(block_table[1:]):
            if b == None:
                file_no = self.EMPTY_BLOCK
            else:
                file_no = b

            self.header_block.block_alloc_table[i] = file_no

        header_block.data = bread.write(
            self.header_block, bread_spec.compressed_sav_file)

        assert len(header_block.data) == blockutils.BLOCK_SIZE, \
            "Header block isn't the expected length; expected 0x%x, got 0x%x" \
            % (blockutils.BLOCK_SIZE, len(header_block.data))

        block_map = factory.blocks

        empty_block_data = []
        for i in xrange(blockutils.BLOCK_SIZE):
            empty_block_data.append(0)

        callback("Writing data to file", current_step, total_steps, True)
        current_step += 1
        for i in xrange(num_blocks):
            if i in block_map:
                data_list = block_map[i].data
            else:
                data_list = empty_block_data

            fp.write(bytearray(data_list))

        callback("Save complete!", total_steps, total_steps, True)

    def save(self, filename, callback=_noop_callback):
        with open(filename, 'wb') as fp:
            self._save(fp, callback)

if __name__ == "__main__":
    sav = SAVFile(sys.argv[1])
    sav.save(sys.argv[2])
