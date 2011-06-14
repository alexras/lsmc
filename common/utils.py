import os
import warnings
import sys
from struct import pack, unpack

def binary_uint_pack_str(length, quantity):
    unpack_str = ">%d" % (quantity)
    if length == 1:
        unpack_str += "B"
    elif length == 2:
        unpack_str += "H"
    elif length == 4:
        unpack_str += "L"
    elif length == 8:
        unpack_str += "Q"
    else:
        assert False, "Don't know how to read a binary number that's %d " \
            "bytes long" % length

    return unpack_str

def binary_uint(int_str, length, quantity):
    unpack_str = binary_uint_pack_str(length, quantity)
    return unpack(unpack_str, int_str)


def binary_read_uint(fp, length):
    return binary_uint(fp.read(length), length, 1)[0]

def binary_read_uint_list(fp, length, quantity):
    return binary_uint(fp.read(length * quantity), length, quantity)

def binary_write_uint(fp, num, length):
    pack_str = binary_uint_pack_str(length, 1)
    fp.write(pack(pack_str, num))

def binary_write_uint_list(fp, uint_list, uint_length):
    pack_str = binary_uint_pack_str(uint_length, len(uint_list))
    packed = pack(pack_str, *uint_list)
    fp.write(packed)

def get_bits(byte):
    bits = []

    tmp_byte = byte

    for i in xrange(8):
        bits.insert(0, tmp_byte % 2)
        tmp_byte /= 2

    return bits

def get_byte(bits):
    byte = 0
    for i in xrange(8):
        byte = byte | (bits[i] * (2 ** (7 - i)))

    return byte

def check_mem_init_flag(raw_data, first_byte_loc, second_byte_loc):
    mem_init_flag = raw_data[first_byte_loc:second_byte_loc + 1]
    ref_mem_flag = [ord('r'), ord('b')]
    if mem_init_flag != ref_mem_flag:
        assert False, ".sav file appears to be corrupted; mem. init flag " \
            "mismatch (s/b %s, is %s)" % (ref_mem_flag, mem_init_flag)


def strip_nulls(string):
    try:
        string = string[:string.index('\x00')]
    except ValueError:
        # No null characters found, pass the string unaltered
        pass

    return string

def make_unique_filename(prefix, suffix, parent):
    filename_prefix = os.path.join(parent, prefix)

    normal_filename = "%s%s" % (filename_prefix, suffix)

    if not os.path.exists(normal_filename):
        return normal_filename

    i = 1

    while True:
        indexed_filename = "%s_%d%s" % (filename_prefix, i, suffix)

        if not os.path.exists(indexed_filename):
            return indexed_filename

        i += 1

def string_to_bytes(string, length):
    if string == None:
        string = ""
    bytes = [ord(x) for x in list(string)]

    for i in xrange(length - len(bytes)):
        bytes.append(0)

    return bytes

def extract_bits(byte, start_bit, end_bit):
    """
    Extract the bits in [start_bit, end_bit] from the byte and return them as
    an integer
    """
    mask = _get_mask(start_bit, end_bit)
    return (byte & mask) >> start_bit

def inject_bits(dest_byte, source_byte,
                start_bit, end_bit):
    """
    Inject a set of bits from one byte into another byte
    """

    source_length = end_bit - start_bit + 1

    source_mask = _get_mask(0, source_length - 1)
    dest_mask = _get_mask(start_bit, end_bit)

    # Invert destination mask so that bits to be replaced get masked out
    dest_mask = dest_mask ^ (2 ** 8 - 1)

    # Mask off source and shift into position
    source_byte = source_byte & source_mask
    source_byte = source_byte << start_bit

    # Mask off dest
    dest_byte = dest_byte & dest_mask

    # Merge source into destination
    return dest_byte | source_byte

def _get_mask(start_bit, end_bit):
    """
    Generate a mask that will mask off bits all bits in the range
    [start_bit, end_bit]
    """

    assert start_bit <= end_bit, "Start bit must be less than end bit"

    num_bits = end_bit - start_bit + 1
    mask = (2 ** num_bits) - 1
    mask = mask << start_bit
    return mask

def byte_to_binary_string(byte):
    return ''.join([str(x) for x in get_bits(byte)])
