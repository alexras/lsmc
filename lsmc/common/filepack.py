import bread
import bread_spec
import itertools

# Byte used to denote run-length encoding
RLE_BYTE = 0xc0

# Byte used to denote special action
SPECIAL_BYTE = 0xe0

# Byte used to denote end of file (appears after special byte)
EOF_BYTE = 0xff

# Byte used to denote default instrument
DEFAULT_INSTR_BYTE = 0xf1

# Byte used to denote default wave
DEFAULT_WAVE_BYTE = 0xf0

DEFAULT_WAVE = bytearray(
    [0x8e, 0xcd, 0xcc, 0xbb, 0xaa, 0xa9, 0x99, 0x88, 0x87, 0x76,
     0x66, 0x55, 0x54, 0x43, 0x32, 0x31])

DEFAULT_INSTRUMENT_FILEPACK = bytearray([
    0xa8, 0, 0, 0xff, 0, 0, 3, 0, 0, 0xd0, 0, 0, 0, 0xf3, 0, 0])

DEFAULT_INSTRUMENT = bytearray([
    0, 0xa8, 0, 0, 0xff, 0, 0, 3, 0, 0, 0xd0, 0, 0, 0, 0xf3, 0])

# DEFAULT_INSTRUMENT = [
#     0xa8, 0, 0, 0xff, 0, 0, 3, 0, 0, 0xd0, 0, 0, 0, 0xf3, 0, 0]

RESERVED_BYTES = [SPECIAL_BYTE, RLE_BYTE]

SPECIAL_DEFAULTS = [DEFAULT_INSTR_BYTE, DEFAULT_WAVE_BYTE]

STATE_BYTES = 0
STATE_RLE_BYTE = 1
STATE_RLE_COUNT = 2
STATE_SPECIAL_BYTE = 3
STATE_DEFAULT_INSTR = 4
STATE_DEFAULT_WAVE = 5
STATE_DONE = 6

def split(compressed_data, segment_size, block_factory):
    # Split compressed data into blocks
    segments = []

    current_segment_start = 0
    index = 0
    data_size = len(compressed_data)

    while index < data_size:
        current_byte = compressed_data[index]

        if index < data_size - 1:
            next_byte = compressed_data[index + 1]
        else:
            next_byte = None

        jump_size = 1

        if current_byte == RLE_BYTE:
            assert next_byte is not None, "Expected a command to follow " \
                "RLE byte"
            if next_byte == RLE_BYTE:
                jump_size = 2
            else:
                jump_size = 3

        elif current_byte == SPECIAL_BYTE:
            assert next_byte is not None, "Expected a command to follow " \
                "special byte"

            if next_byte == SPECIAL_BYTE:
                jump_size = 2
            elif next_byte == DEFAULT_INSTR_BYTE or \
                    next_byte == DEFAULT_WAVE_BYTE:
                jump_size = 3
            else:
                assert False, "Encountered unexpected EOF or block " \
                    "switch while segmenting"

        # Need two bytes for the jump or EOF
        if index - current_segment_start + jump_size > segment_size - 2:
            segments.append(compressed_data[
                    current_segment_start:index])

            current_segment_start = index
        else:
            index += jump_size

    # Append the last segment, if any
    if current_segment_start != index:
        segments.append(compressed_data[
                current_segment_start:current_segment_start + index])


    # Make sure that no data was lost while segmenting
    total_segment_length = sum(map(len, segments))
    assert total_segment_length == len(compressed_data), "Lost %d bytes of " \
        "data while segmenting" % (len(compressed_data) - total_segment_length)

    block_ids = []

    for segment in segments:
        block = block_factory.new_block()
        block_ids.append(block.id)

    for (i, segment) in enumerate(segments):
        block = block_factory.blocks[block_ids[i]]

        assert len(block.data) == 0, "Encountered a block with "
        "pre-existing data while writing"

        if i == len(segments) - 1:
            # Write EOF to the end of the segment
            add_eof(segment)
        else:
            # Write a pointer to the next segment
            add_block_switch(segment, block_ids[i + 1])

        # Pad segment with zeroes until it's large enough
        pad(segment, segment_size)

        block.data = segment

    return block_ids

def renumber_block_keys(blocks):
    # There is an implicit block switch to the 0th block at the start of the
    # file
    byte_switch_keys = [0]
    block_keys = blocks.keys()

    # Scan the blocks, recording every block switch statement
    for block in blocks.values():
        i = 0
        while i < len(block.data) - 1:
            current_byte = block.data[i]
            next_byte = block.data[i + 1]

            if current_byte == RLE_BYTE:
                if next_byte == RLE_BYTE:
                    i += 2
                else:
                    i += 3
            elif current_byte == SPECIAL_BYTE:
                if next_byte in SPECIAL_DEFAULTS:
                    i += 3
                elif next_byte == SPECIAL_BYTE:
                    i += 2
                else:
                    if next_byte != EOF_BYTE:
                        byte_switch_keys.append(next_byte)

                    break

            else:
                i += 1

    byte_switch_keys.sort()
    block_keys.sort()

    assert len(byte_switch_keys) == len(block_keys), (
        "Number of blocks that are target of block switches (%d) "
        % (len(byte_switch_keys)) +
        "does not equal number of blocks in the song (%d)"
        % (len(block_keys)) +
        "; possible corruption")

    if byte_switch_keys == block_keys:
        # No remapping necessary
        return blocks

    new_block_map = {}

    for block_key, byte_switch_key in itertools.izip(
            block_keys, byte_switch_keys):

        new_block_map[byte_switch_key] = blocks[block_key]

    return new_block_map

def merge(blocks):
    current_block = blocks[sorted(blocks.keys())[0]]

    compressed_data = []
    eof = False

    while not eof:
        data_size_to_append = None
        next_block = None

        i = 0
        while i < len(current_block.data) - 1:
            current_byte = current_block.data[i]
            next_byte = current_block.data[i + 1]

            if current_byte == RLE_BYTE:
                if next_byte == RLE_BYTE:
                    i += 2
                else:
                    i += 3
            elif current_byte == SPECIAL_BYTE:
                if next_byte in SPECIAL_DEFAULTS:
                    i += 3
                elif next_byte == SPECIAL_BYTE:
                    i += 2
                else:
                    data_size_to_append = i

                    # hit end of file
                    if next_byte == EOF_BYTE:
                        eof = True
                    else:
                        next_block = blocks[next_byte]

                    break
            else:
                i += 1

        assert data_size_to_append is not None, "Ran off the end of a "\
            "block without encountering a block switch or EOF"

        compressed_data.extend(current_block.data[0:data_size_to_append])

        if not eof:
            assert next_block is not None, "Switched blocks, but did " \
                "not provide the next block to switch to"

            current_block = next_block

    return compressed_data

def add_eof(segment):
    segment.extend([SPECIAL_BYTE, EOF_BYTE])

def add_block_switch(segment, block_id):
    segment.extend([SPECIAL_BYTE, block_id])

def pad(segment, size):
    for i in xrange(size - len(segment)):
        segment.append(0)

    assert len(segment) == size

def decompress(compressed_data):
    raw_data = []

    index = 0

    while index < len(compressed_data):
        current = compressed_data[index]
        index += 1

        if current == RLE_BYTE:
            directive = compressed_data[index]
            index += 1

            if directive == RLE_BYTE:
                raw_data.append(RLE_BYTE)
            else:
                count = compressed_data[index]
                index += 1

                raw_data.extend([directive] * count)
        elif current == SPECIAL_BYTE:
            directive = compressed_data[index]
            index += 1

            if directive == SPECIAL_BYTE:
                raw_data.append(SPECIAL_BYTE)
            elif directive == DEFAULT_WAVE_BYTE:
                count = compressed_data[index]
                index += 1

                raw_data.extend(DEFAULT_WAVE * count)
            elif directive == DEFAULT_INSTR_BYTE:
                count = compressed_data[index]
                index += 1

                raw_data.extend(DEFAULT_INSTRUMENT_FILEPACK * count)
            elif directive == EOF_BYTE:
                assert False, ("Unexpected EOF command encountered while "
                               "decompressing")
            else:
                assert False, "Countered unexpected sequence 0x%02x 0x%02x" % (
                    current, directive)
        else:
            raw_data.append(current)

    return raw_data

def compress(raw_data, test=False):
    raw_data = bytearray(raw_data)
    compressed_data = []

    data_index = 0
    data_size = len(raw_data)

    index = 0
    next_bytes = [-1, -1, -1]

    def is_default_instrument(index):
        if index + len(DEFAULT_INSTRUMENT_FILEPACK) > len(raw_data):
            return False

        instr_bytes = raw_data[index:index + len(DEFAULT_INSTRUMENT_FILEPACK)]

        if instr_bytes[0] != 0xa8 or instr_bytes[1] != 0:
            return False

        return instr_bytes == DEFAULT_INSTRUMENT_FILEPACK

    def is_default_wave(index):
        return (index + len(DEFAULT_WAVE) <= len(raw_data) and
                raw_data[index:index + len(DEFAULT_WAVE)] == DEFAULT_WAVE)

    while index < data_size:
        current_byte = raw_data[index]

        for i in xrange(3):
            if index < data_size - (i + 1):
                next_bytes[i] = raw_data[index + (i + 1)]
            else:
                next_bytes[i] = -1

        if current_byte == RLE_BYTE:
            compressed_data.append(RLE_BYTE)
            compressed_data.append(RLE_BYTE)
            index += 1
        elif current_byte == SPECIAL_BYTE:
            compressed_data.append(SPECIAL_BYTE)
            compressed_data.append(SPECIAL_BYTE)
            index += 1
        elif is_default_instrument(index):
            counter = 1
            index += len(DEFAULT_INSTRUMENT_FILEPACK)

            while (is_default_instrument(index) and
                   counter < 0x100):
                counter += 1
                index += len(DEFAULT_INSTRUMENT_FILEPACK)

            compressed_data.append(SPECIAL_BYTE)
            compressed_data.append(DEFAULT_INSTR_BYTE)
            compressed_data.append(counter)

        elif is_default_wave(index):
            counter = 1
            index += len(DEFAULT_WAVE)

            while is_default_wave(index) and counter < 0xff:
                counter += 1
                index += len(DEFAULT_WAVE)

            compressed_data.append(SPECIAL_BYTE)
            compressed_data.append(DEFAULT_WAVE_BYTE)
            compressed_data.append(counter)

        elif (current_byte == next_bytes[0] and
              next_bytes[0] == next_bytes[1] and
              next_bytes[1] == next_bytes[2]):
            # Do RLE compression

            compressed_data.append(RLE_BYTE)
            compressed_data.append(current_byte)
            counter = 0

            while (index < data_size and
                   raw_data[index] == current_byte and
                   counter < 0xff):
                index += 1
                counter += 1

            compressed_data.append(counter)
        else:
            compressed_data.append(current_byte)
            index += 1

    return compressed_data
