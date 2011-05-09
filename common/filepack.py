import instrument
import wave

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


RESERVED_BYTES = [SPECIAL_BYTE, RLE_BYTE]

STATE_BYTES = 0
STATE_RLE_BYTE = 1
STATE_RLE_COUNT = 2
STATE_SPECIAL_BYTE = 3
STATE_DEFAULT_INSTR = 4
STATE_DEFAULT_WAVE = 5
STATE_DONE = 6

def split(compressed_data, segment_size):
    # Split compressed data into roughly block-sized segments
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

    return segments

def merge(segments):
        current_segment = segments[sorted(segments.keys())[0]]

        compressed_data = []
        eof = False

        ignored_special_commands = [DEFAULT_INSTR_BYTE,
                                    DEFAULT_WAVE_BYTE]

        while not eof:
            data_size_to_append = None
            next_segment = None

            i = 0
            while i < len(current_segment) - 1:
                current_byte = current_segment[i]
                next_byte = current_segment[i + 1]

                if current_byte == RLE_BYTE:
                    if next_byte == RLE_BYTE:
                        i += 2
                    else:
                        i += 3
                elif current_byte == SPECIAL_BYTE:
                    if next_byte in ignored_special_commands:
                        i += 3
                    elif next_byte == SPECIAL_BYTE:
                        i += 2
                    else:
                        data_size_to_append = i

                        # hit end of file
                        if next_byte == EOF_BYTE:
                            eof = True
                        else:
                            next_segment = segments[next_byte]

                        break
                else:
                    i += 1

            assert data_size_to_append is not None, "Ran off the end of a "\
                "segment without encountering a segment switch or EOF"

            compressed_data.extend(current_segment[0:data_size_to_append])

            if not eof:
                assert next_segment is not None, "Switched segments, but did " \
                    "not provide the next segment to switch to"

                current_segment = next_segment

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

    state = STATE_BYTES

    rle_byte_value = None

    index = 0
    data_size = len(compressed_data)

    while index < data_size:
        data_byte = compressed_data[index]
        index += 1

        if state == STATE_BYTES:
            if data_byte == RLE_BYTE:
                state = STATE_RLE_BYTE
            elif data_byte == SPECIAL_BYTE:
                state = STATE_SPECIAL_BYTE
            else:
                raw_data.append(data_byte)

        elif state == STATE_RLE_BYTE:
            if data_byte == RLE_BYTE:
                raw_data.append(data_byte)
                state = STATE_BYTES
            else:
                rle_byte_value = data_byte
                state = STATE_RLE_COUNT

        elif state == STATE_RLE_COUNT:
            for i in xrange(data_byte):
                raw_data.append(rle_byte_value)
            state = STATE_BYTES

        elif state == STATE_SPECIAL_BYTE:
            if data_byte == SPECIAL_BYTE:
                raw_data.append(data_byte)
                state = STATE_BYTES
            elif data_byte == DEFAULT_INSTR_BYTE:
                state = STATE_DEFAULT_INSTR
            elif data_byte == DEFAULT_WAVE_BYTE:
                state = STATE_DEFAULT_WAVE
            else:
                assert False, "Didn't expect to encounter special "\
                    "instruction byte 0x%x while decompressing" % \
                    (data_byte)

        elif state == STATE_DEFAULT_INSTR:
            for i in xrange(data_byte):
                raw_data.extend(instrument.DEFAULT)

            state = STATE_BYTES
        elif state == STATE_DEFAULT_WAVE:
            for i in xrange(data_byte):
                raw_data.extend(wave.DEFAULT)

            state = STATE_BYTES
        else:
            assert False, "Encountered invalid state %d" % (state)

    return raw_data


def compress(raw_data):
    compressed_data = []

    data_index = 0
    data_size = len(raw_data)

    while data_index < data_size:
        # If we encounter the default instrument at this point in the file,
        # turn it into the abbreviated default instrument

        # If we encounter the default instrument at this point in the file,
        # use the abbreviated representation for the default instrument

        if raw_data[data_index:data_index + instrument.NUM_PARAMS] == \
                instrument.DEFAULT:
            compressed_data.extend([SPECIAL_BYTE, DEFAULT_INSTR_BYTE])
            data_index += instrument.NUM_PARAMS

        # If we encounter the default wave at this point in the file, use
        # the abbreviated representation for the default wave

        elif raw_data[data_index:data_index + wave.NUM_FRAMES] == \
                wave.DEFAULT:
            compressed_data.extend([SPECIAL_BYTE, DEFAULT_WAVE_BYTE])
            data_index += wave.NUM_FRAMES

        # Otherwise we're just dealing with bytes
        else:
            current_byte = raw_data[data_index]

            # Do a lookahead to see how many identical bytes are at this
            # point in the stream
            lookahead_index = data_index

            while lookahead_index < data_size and \
                    raw_data[lookahead_index] == current_byte:
                lookahead_index += 1

            # If you have more than three identical bytes, doing run-length
            # encoding is worth it; otherwise, just write the raw bytes and
            # move on. If you have 256 or more bytes, will have to RLE
            # multiple times

            num_occurrences = min(lookahead_index - data_index, 255)

            # If you're writing a reserved byte (i.e. a command specifier)
            # you'll have to write each occurrence of the byte twice to
            # avoid it being interpreted as a control character
            if current_byte in RESERVED_BYTES:
                num_occurrences *= 2

            if num_occurrences > 3:
                compressed_data.extend([RLE_BYTE, current_byte,
                                        num_occurrences])
            else:
                for i in xrange(num_occurrences):
                    compressed_data.append(current_byte)

            data_index += num_occurrences

    return compressed_data
