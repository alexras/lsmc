import sys

class Project(object):
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

    # Binary data for default instrument
    DEFAULT_INSTR = [0xa8, 0, 0, 0xff, 0, 0, 3, 0, 0, 0xd0, 0, 0, 0, 0xf3, 0, 0]

    # Binary data for default wave
    DEFAULT_WAVE = [0x8e, 0xcd, 0xcc, 0xbb, 0xaa, 0xa9, 0x99, 0x88, 0x87, 0x76,
                    0x66, 0x55, 0x54, 0x43, 0x32, 0x31]

    # State machine states for __init__
    STATE_BYTES = 0
    STATE_RLE_BYTE = 1
    STATE_RLE_COUNT = 2
    STATE_SPECIAL_BYTE = 3
    STATE_DEFAULT_INSTR = 4
    STATE_DEFAULT_WAVE = 5
    STATE_DONE = 6

    def __init__(self, name, version, blocks):
        self.name = name
        self.version = version

        self.parse_blocks(blocks)

    def parse_blocks(self, blocks):
        raw_data = []

        state = self.STATE_BYTES

        current_block_index = sorted(blocks.keys())[0]
        current_block = blocks[current_block_index]
        current_block_offset = 0

        rle_byte_value = None

        while state != self.STATE_DONE:
            data_byte = current_block[current_block_offset]
            current_block_offset += 1

            if state == self.STATE_BYTES:
                if data_byte == self.RLE_BYTE:
                    state = self.STATE_RLE_BYTE
                elif data_byte == self.SPECIAL_BYTE:
                    state = self.STATE_SPECIAL_BYTE
                else:
                    raw_data.append(data_byte)

            elif state == self.STATE_RLE_BYTE:
                if data_byte == self.RLE_BYTE:
                    raw_data.append(data_byte)
                    state = self.STATE_BYTES
                else:
                    rle_byte_value = data_byte
                    state = self.STATE_RLE_COUNT

            elif state == self.STATE_RLE_COUNT:
                for i in xrange(data_byte):
                    raw_data.append(rle_byte_value)
                state = self.STATE_BYTES

            elif state == self.STATE_SPECIAL_BYTE:
                if data_byte == self.SPECIAL_BYTE:
                    raw_data.append(data_byte)
                    state = self.STATE_BYTES
                elif data_byte == self.DEFAULT_INSTR_BYTE:
                    state = self.STATE_DEFAULT_INSTR
                elif data_byte == self.DEFAULT_WAVE_BYTE:
                    state = self.STATE_DEFAULT_WAVE
                elif data_byte == self.EOF_BYTE:
                    # End of file reached; can stop parsing
                    state = self.STATE_DONE
                else:
                    current_block_index = data_byte
                    current_block = blocks[current_block_index]
                    current_block_offset = 0
                    state = self.STATE_BYTES

            elif state == self.STATE_DEFAULT_INSTR:
                for i in xrange(data_byte):
                    raw_data.extend(self.DEFAULT_INSTR)

                state = self.STATE_BYTES
            elif state == self.STATE_DEFAULT_WAVE:
                for i in xrange(data_byte):
                    raw_data.extend(self.DEFAULT_WAVE)

                state = self.STATE_BYTES
            else:
                sys.exit("Encountered invalid state %d" % (state))
