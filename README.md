# Stegosaurus
A simple command line-based Python program to implement steganographic algorithms.

## Getting Started
This program requires Pillow, a graphics processing library for Python 3, a fork of the Python Imaging Library for Python 2. You can view the Github page [here](https://github.com/python-pillow/Pillow).

## Supported Algorithms
### LSB
Currently, the only supported algorithm is least significant bit steganography, which replaces the two least significant bits in the RGBA channels of each pixel to store the bytes of a message.