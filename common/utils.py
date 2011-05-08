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
        sys.exit("Don't know how to read a binary number that's %d bytes long",
                 length)

    return unpack_str

def binary_uint(int_str, length, quantity):
    unpack_str = binary_uint_pack_str(length, quantity)
    return unpack(unpack_str, int_str)


def binary_read_uint(fp, length):
    return binary_uint(fp.read(length), length, 1)[0]

def binary_write_uint(fp, num, length):
    pack_str = binary_uint_pack_str(length, 1)
    fp.write(pack(pack_str, num))

def binary_write_uint_list(fp, uint_list, uint_length):
    pack_str = binary_uint_pack_str(uint_length, len(uint_list))
    fp.write(pack(pack_str, *uint_list))

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
        print byte

    return byte

def check_mem_init_flag(raw_data, first_byte_loc, second_byte_loc):
    mem_init_flag = "".join([chr(x) for x in
                             raw_data[first_byte_loc:second_byte_loc + 1]])


    if mem_init_flag != "rb":
        sys.exit(".sav file appears to be corrupted; mem. init flag "
                 "mismatch (s/b 'rb', is '%s')" % (mem_init_flag))

