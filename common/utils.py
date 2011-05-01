import sys
from struct import unpack

def binary_uint(int_str, length, quantity):
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

    return unpack(unpack_str, int_str)


def binary_read_uint(fp, length):
    return binary_uint(fp.read(length), length, 1)[0]
