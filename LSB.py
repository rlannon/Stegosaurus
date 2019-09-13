"""

LSB.py

The algorithm for least significant bit steganography

"""

from PIL import Image


def hide_message(image, message):
    """Puts 'message' in an image 'image'. First, the algorithm checks to see whether the image is big enough to contain
    the message. If not, it prints an error message and returns None; if it can, it stores the message in the 2 least
    significant bytes of each pixel's RGBA values.
    Message can be any format; image must be a PIL image object.
    This function returns the modified image object.
    The header of the file contains a 3-byte header, 4 bytes for the message length, and 1 byte for is_string"""

    print("Hiding message...")
    image = image.convert("RGBA")

    # Message size must be smaller than (number of pixels - 5); we need 4 for the length and 1 for bool is_string
    print("Checking to see if image can store message of size", message.__sizeof__())
    if message.__sizeof__() * 4 > (image.width * image.height) - 5:
        # Message is too large for the image
        print("error: message is too large\n"
              "maximum size is", image.width*image.height - 5, "bytes; your message is", message.__sizeof__(), "bytes")
        return None
    else:
        print("Image can store message")

        # First, we must encode our message as a series of immutable bytes
        # Whether we encode will depend on whether the message type is "str" or not
        print("Checking message format...")
        print("Encoding message...")
        if type(message) is str:
            message = bytes(message, 'utf-8')
            is_string = True
        elif type(message) is int:
            message = message.to_bytes(message.__sizeof__(), byteorder="big", signed=True)
            is_string = False
        else:
            message = bytearray(message)
            is_string = False

        # Next, we store the length of our original message as big-endian, unsigned bytes
        # Since it is a byte array, we can use __len__()
        org_msg_len = message.__len__().to_bytes(4, byteorder="big", signed=False)

        # Next, declare our length array; this will store our length data in 16 binary numbers (len is 4 bytes)
        len_array = []

        # Next, initialize our position counters; these will tell us where in the message we are
        len_array_position = 0
        msg_byte_position = 0

        # Next, we will populate our len_array with the properly formatted org_msg_len (only last 2 bits will contain
        # information; all other bits are not used because we are only using the last two bits in a pixel's bytes)
        print("Creating steganographic length data...")
        for byte_num in range(0, 4):   # Message is four bytes long
            len_array.append(org_msg_len[byte_num] & 0b11000000)   # catch only two bits from the byte,
            len_array.append(org_msg_len[byte_num] & 0b00110000)   # storing them in their own byte in len_array
            len_array.append(org_msg_len[byte_num] & 0b00001100)
            len_array.append(org_msg_len[byte_num] & 0b00000011)

            # Now, we must properly shift the bits we just wrote
            for j in range(0, 4):
                shift_amount = 6 - (2 * j)
                # Don't shift the first four bytes in the array every time; shift the correct byte as byte_num increases
                len_array[byte_num*4 + j] = len_array[byte_num*4 + j] >> shift_amount

        # Next, create our steg message byte array; this will contain the message two bits at a time
        steg_msg_bytes = []
        temp_bytes = []   # used to temporarily hold our bytes until we put them in the steg_msg_bytes bytearray

        print("Creating steganographic message data...")
        for byte_num in range(0, message.__len__()):
            temp_bytes.clear()  # clear for the next byte we are reading in from the message

            temp_bytes.append(message[byte_num] & 0b11000000)   # catch only two bits from the byte,
            temp_bytes.append(message[byte_num] & 0b00110000)   # storing them in their own byte in the array
            temp_bytes.append(message[byte_num] & 0b00001100)
            temp_bytes.append(message[byte_num] & 0b00000011)

            for i in range(0, 4):
                shift_amount = 6 - (2 * i)  # each bit must shift a different amount
                temp_bytes[i] = temp_bytes[i] >> shift_amount   # shift so that each byte's 2 lsbs are the bits we want
                steg_msg_bytes.append(temp_bytes[i])

        #
        # Now, write the data to the image's pixels
        #
        count = 0

        print("Writing data to image...")

        for row in range(0, image.height):
            for col in range(0, image.width):
                # We need to get the pixel data in every loop, so do it at the top
                # We will store our pixel values in a list so we only need to access it once
                pixel_data = image.getpixel((col, row))

                # Create an identical pixel, but drop last two bits
                new_red = pixel_data[0] & 0b11111100
                new_green = pixel_data[1] & 0b11111100
                new_blue = pixel_data[2] & 0b11111100
                new_alpha = pixel_data[3] & 0b11111100

                # Write our length data to the first four bytes
                if row == 0 and col < 4:
                    # Set the new pixel values to be the old pixel values plus the values in our length array
                    # Since the old values were xxxxxx00, and the new values are 000000xx,
                    # we will get the correct information when we add them
                    new_red = new_red + len_array[len_array_position]
                    new_green = new_green + len_array[len_array_position + 1]
                    new_blue = new_blue + len_array[len_array_position + 2]
                    new_alpha = new_alpha + len_array[len_array_position + 3]

                    # put our pixel data
                    image.putpixel((col, row), (new_red, new_green, new_blue, new_alpha))

                    # increment our position by four, as we used four bytes from len_array
                    len_array_position += 4

                # our is_string bool will be stored in the red value of the fifth pixel
                elif row == 0 and col == 4:

                    if is_string:
                        new_red = new_red + 1
                    else:
                        pass

                    image.putpixel((col, row), (new_red, new_green, new_blue, new_alpha))

                # Do for every other pixel
                else:
                    if msg_byte_position <= ((message.__len__() * 4) - 4):  # because it takes 4 pixels per byte
                        new_red = new_red + steg_msg_bytes[msg_byte_position]
                        new_green = new_green + steg_msg_bytes[msg_byte_position + 1]
                        new_blue = new_blue + steg_msg_bytes[msg_byte_position + 2]
                        new_alpha = new_alpha + steg_msg_bytes[msg_byte_position + 3]

                        # store the modified pixel back where it came from
                        image.putpixel((col, row), (new_red, new_green, new_blue, new_alpha))

                        # increment our msg_byte_position so the next byte from steg_msg_bytes is the proper one
                        msg_byte_position += 4
                        count += 1
    print("Done.")
    return image


def reveal_message(image):
    """Takes an image object as parameter and returns the steganographic message within."""
    len_array = []
    msg_len = 0
    byte_ptr = 0
    is_string = False
    msg_byte_array = bytearray()

    print("Fetching message...")

    for row in range(0, image.height):
        for col in range(0, image.width):
            pixel_data = image.getpixel((col, row))

            if row == 0 and col < 4:
                for byte in range(0, 4):    # length is 4 bytes
                    len_array.append(pixel_data[byte] & 0b00000011)
            elif row == 0 and col == 4:
                for i in range(0, 16):  # 16 bit-pairs
                    shift_amount = 30 - (2 * i)
                    msg_len += len_array[i] << shift_amount
                if pixel_data[0] & 0b00000011 is not 0:
                    is_string = True
                else:
                    is_string = False
            else:
                if byte_ptr < msg_len:
                    red_steg_bits = (pixel_data[0] & 0b00000011) << 6
                    green_steg_bits = (pixel_data[1] & 0b00000011) << 4
                    blue_steg_bits = (pixel_data[2] & 0b00000011) << 2
                    alpha_steg_bits = (pixel_data[3] & 0b00000011) << 0

                    msg_byte_array.append(red_steg_bits + green_steg_bits + blue_steg_bits + alpha_steg_bits)

                    byte_ptr += 1
    if is_string:
        return str(msg_byte_array, encoding='utf-8')
    else:
        return bytearray(msg_byte_array)
