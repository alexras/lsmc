import blocks
import instrument
import wave

# Maximum size of a block
BLOCK_SIZE = 0x200

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

class Block(object):
    def __init__(self, block_id, data):
        self.id = block_id
        self.data = data
        self.offset = 0

    def __repr__(self):
        data_str_list = []

        i = 0

        while i < len(self.data):
            curr_byte = self.data[i]

            if i + 1 < len(self.data):
                next_byte = self.data[i + 1]
            else:
                next_byte = None

            if i + 2 < len(self.data):
                next_next_byte = self.data[i + 2]
            else:
                next_next_byte = None

            if curr_byte == SPECIAL_BYTE:
                assert next_byte != None, "Incomplete special instruction"

                if next_byte == SPECIAL_BYTE:
                    data_str_list.append("0x%x" % (SPECIAL_BYTE))
                    i += 2
                elif next_byte == DEFAULT_INSTR_BYTE:
                    assert next_next_byte != None, \
                        "Incomplete default instrument instruction"

                    data_str_list.append("DEFAULT INSTR x%d" %
                                         (next_next_byte))
                    i += 3
                elif next_byte == DEFAULT_WAVE_BYTE:
                    assert next_next_byte != None, \
                        "Incomplete default wave instruction"
                    data_str_list.append("DEFAULT_WAVE x%d" %
                                         (next_next_byte))
                    i += 3
                elif next_byte == EOF_BYTE:
                    data_str_list.append("EOF")
                    i += 2
                else:
                    data_str_list.append("SWITCH BLOCK %d" % (next_byte))
                    i += 2
            elif curr_byte == RLE_BYTE:
                assert next_byte != None, "Incomplete RLE instruction"

                if next_byte == RLE_BYTE:
                    data_str_list.append("0x%x" % (RLE_BYTE))
                    i += 2
                else:
                    assert next_next_byte != None, "Incomplete RLE instruction"
                    data_str_list.append("0x%x x%d"
                                         % (next_byte, next_next_byte))
                    i += 3
            else:
                data_str_list.append("0x%x" % (curr_byte))
                i += 1

        repr_str = "BLOCK %d\n" % (self.id)
        repr_str = str(data_str_list)


class BlockFactory(object):
    def __init__(self):
        self.max_id = 0
        self.blocks = {}

    def new_block(self):
        block = Block(self.max_id, [])
        self.blocks[self.max_id] = block
        self.max_id += 1

        return block

class BlockWriter(object):
    def write(self, raw_data, factory):
        data_index = 0
        data_size = len(raw_data)

        compressed_data = []

        # Cache the points in the data where we can safely subdivide a block
        valid_cutoff_points = []

        while data_index < data_size:
            valid_cutoff_points.append(len(compressed_data))

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

            # If we are considering a special byte, write two of it so we don't
            # get confused

            elif raw_data[data_index] == SPECIAL_BYTE:
                compressed_data.extend([SPECIAL_BYTE, SPECIAL_BYTE])
                data_index += 1
            elif raw_data[data_index] == RLE_BYTE:
                compressed_data.extend([RLE_BYTE, RLE_BYTE])
                data_index += 1

            # Otherwise we're just dealing with some normal bytes
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

                num_occurrences = min(lookahead_index - data_index + 1, 255)

                if num_occurrences > 3:
                    compressed_data.extend([RLE_BYTE, current_byte,
                                            num_occurrences])
                else:
                    for i in xrange(num_occurrences):
                        compressed_data.append(current_byte)

                data_index += num_occurrences

        block_ids_for_file = []

        # Want at least 2 bytes left over at the end for the block switch
        # instruction
        target_chunk_size = blocks.BLOCK_SIZE - 2

        cutoff_point_index = 0

        block_data_indices = []

        last_cutoff_point = 0

        while cutoff_point_index < len(valid_cutoff_points):
            curr_cutoff_point = valid_cutoff_points[cutoff_point_index]

            if cutoff_point_index == len(valid_cutoff_points) - 1:
                next_cutoff_point = None
            else:
                next_cutoff_point = valid_cutoff_points[cutoff_point_index + 1]

            # If last cutoff point reached, have to make a block.

            at_last_cutoff_point = (next_cutoff_point == None)

            # If this is the largest cutoff that's smaller than the target,
            # should make a block
            curr_cutoff_point_small_enough = \
                (curr_cutoff_point - last_cutoff_point <= target_chunk_size)
            next_cutoff_point_too_large = next_cutoff_point == None or \
                (next_cutoff_point - last_cutoff_point > target_chunk_size)

            if at_last_cutoff_point or (curr_cutoff_point_small_enough and
                                        next_cutoff_point_too_large):
                block = factory.new_block()
                block_ids_for_file.append(block.id)

                block.data = compressed_data[
                    last_cutoff_point:curr_cutoff_point]

                last_cutoff_point = curr_cutoff_point

            cutoff_point_index += 1

        for i in xrange(len(block_ids_for_file)):
            block_id = block_ids_for_file[i]
            block = factory.blocks[block_id]

            if i == len(block_ids_for_file) - 1:
                block.data.extend([SPECIAL_BYTE, EOF_BYTE])
            else:
                block.data.extend([SPECIAL_BYTE, block_ids_for_file[i + 1]])

            for i in xrange(blocks.BLOCK_SIZE - len(block.data)):
                block.data.append(0)

        return block_ids_for_file

class BlockReader(object):
    STATE_BYTES = 0
    STATE_RLE_BYTE = 1
    STATE_RLE_COUNT = 2
    STATE_SPECIAL_BYTE = 3
    STATE_DEFAULT_INSTR = 4
    STATE_DEFAULT_WAVE = 5
    STATE_DONE = 6

    def read(self, block_dict):
        """
        Parses a dictionary of blocks into a raw byte stream
        """
        raw_data = []

        state = self.STATE_BYTES

        current_block_index = sorted(block_dict.keys())[0]
        current_block = block_dict[current_block_index]
        current_block.offset = 0

        rle_byte_value = None

        while state != self.STATE_DONE:
            try:
                data_byte = current_block.data[current_block.offset]
            except IndexError, e:
                print current_block
                raise e
            current_block.offset += 1

            if state == self.STATE_BYTES:
                if data_byte == RLE_BYTE:
                    state = self.STATE_RLE_BYTE
                elif data_byte == SPECIAL_BYTE:
                    state = self.STATE_SPECIAL_BYTE
                else:
                    raw_data.append(data_byte)

            elif state == self.STATE_RLE_BYTE:
                if data_byte == RLE_BYTE:
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
                if data_byte == SPECIAL_BYTE:
                    raw_data.append(data_byte)
                    state = self.STATE_BYTES
                elif data_byte == DEFAULT_INSTR_BYTE:
                    state = self.STATE_DEFAULT_INSTR
                elif data_byte == DEFAULT_WAVE_BYTE:
                    state = self.STATE_DEFAULT_WAVE
                elif data_byte == EOF_BYTE:
                    # End of file reached; can stop parsing
                    state = self.STATE_DONE
                else:
                    current_block_index = data_byte
                    current_block = block_dict[current_block_index]
                    current_block.offset = 0
                    state = self.STATE_BYTES


            elif state == self.STATE_DEFAULT_INSTR:
                for i in xrange(data_byte):
                    raw_data.extend(instrument.DEFAULT)

                state = self.STATE_BYTES
            elif state == self.STATE_DEFAULT_WAVE:
                for i in xrange(data_byte):
                    raw_data.extend(wave.DEFAULT)

                state = self.STATE_BYTES
            else:
                assert False, "Encountered invalid state %d" % (state)

        return raw_data



            # # If a block doesn't exist, create one and give it the appropriate
            # # block ID
            # if current_block == None:
            #     current_block = factory.new_block()
            #     block_ids_for_file.append(current_block.id)

            # # If the block is almost full, create a new block and point the old
            # # block at the new one. Since we will be appending at most 3 bytes
            # # to the block at each step, we make sure that at least three bytes
            # # are always free in the current block
            # if len(current_block.data) >= BLOCK_SIZE - 3:
            #     next_block = factory.new_block()
            #     current_block.data.extend([SPECIAL_BYTE, next_block.id])
            #     current_block = next_block
            #     block_ids_for_file.append(current_block.id)

            # # If we've hit the end of the data, write the EOF bytes
            # if data_index == data_size:
            #     current_block.data.extend([SPECIAL_BYTE, EOF_BYTE])
            #     data_index += 1
            #     continue

            # Otherwise, we have a partially filled block
