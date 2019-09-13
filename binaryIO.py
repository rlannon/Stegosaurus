"""
binaryIO.py
Copyright 2019 Riley Lannon

A small module for handling binary values with file IO in Python
"""

def readU8(file):
    """Reads a single byte from a file"""
    return int.from_bytes(file.read(1), "little")


def readU16(file, end=False):
    """
    readU16(file, end)
    Returns a 16-bit unsigned numeric value.

    :param file:    a file object, open in binary mode, from which to read values
    :param end:     the endianness of the file; False = big, True = little
    :return:        int
    """

    byte_array = []
    byte_array.append(readU8(file))
    byte_array.append(readU8(file))

    if (end):
        # little-endian
        return int.from_bytes(byte_array, "little")
    else:
        # big-endian
        return int.from_bytes(byte_array, "big")


def read_bytes(file, num):
    """
    read_bytes(num)
    reads num bytes from a file

    :param file:    the file object (binary read mode) from which to read
    :param num:     the number of bytes to return
    :return:        list:int
    """

    arr = []
    for i in range(num):
        arr.append(file.read(1))
    return arr


def readU32(file, end=False):
    """
    readU32(file, end)
    Returns a 32-bit unsigned numeric value

    :param file:    the file we wish to read from, opened in binary read mode
    :param end:     the endianness of the file; False = big, True = little
    :return:        int
    """

    byte_array = []
    for i in range(4):
        byte_array.append(readU8(file))

    if (end):
        # little-endian
        return int.from_bytes(byte_array, "little")
    else:
        return int.from_bytes(byte_array, "big")
