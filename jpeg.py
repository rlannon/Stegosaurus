import binaryIO

class InvalidFormatError(Exception):
    def __init__(self, message):
        super(InvalidFormatError, self).__init__(message)
        self.message = message


class JPEG:
    """Contains information for a JPEG file in JFIF format"""

    def __init__(self, filepath):
        # JPEG class data

        # APP0 segment
        self.jfif_version = [0, 0]  # major, minor
        self.density_units = 0  # units for following pixel density fields
        # densities are as follows:
        # 00 - no units (width:height pixel aspect ratio)
        # 01 - pixels per inch
        # 02 - pixels per cm
        self.x_density = 0  # horz. pixel density
        self.y_density = 0  # vert. pixel density
        self.x_thumb = 0    # horz. thumbnail pixel count
        self.y_thumb = 0    # vert. thumbnail pixel count
        self.thumbnail_RGB = []     # uncompressed RGB thumbnail

        # initialization routine
        self.img = open(filepath, "rb")
        self.read_jpeg()

        return

    def read_jpeg(self):
        """Opens a jpeg file and reads it into the jpeg obect"""
        soi = binaryIO.read_bytes(self.img, 2)
        print(soi)
        if soi == [b'\xFF', b'\xD8']:
            print("valid SOI")
            self.read_APP0()
        else:
            raise InvalidFormatError("Invalid bytes for SOI")
        return

    def read_APP0(self):
        """
        read_APP0(self)
        Reads the APP0 section and sets appropriate class data

        :return: None
        """

        # get the APP0 marker "FF E0"
        APP0_marker = binaryIO.read_bytes(self.img, 2)
        if APP0_marker == [b'\xFF', b'\xE0']:
            # valid APP0; begin reading APP0
            APP0_length = binaryIO.readU16(self.img)    # length excluding marker bytes
            identifier = binaryIO.read_bytes(self.img, 5)
            length_counter = 7  # track our length
            # check to ensure identifier was valid
            if identifier == [b'J', b'F', b'I', b'F', b'\00']:
                #   todo: continue reading APP0 section
                version = binaryIO.read_bytes(self.img, 2)
                length_counter += 2
                self.jfif_version[0] = int.from_bytes(version[0], "big")    # get the version
                self.jfif_version[1] = int.from_bytes(version[1], "big")

                self.density_units = binaryIO.readU8(self.img)
                length_counter += 1

                if self.density_units == 0:
                    print("no units")
                elif self.density_units == 1:
                    print("pixels per inch")
                elif self.density_units == 2:
                    print("pixels per centimeter")
                else:
                    raise ValueError("Invalid density unit specifier in APP0")

                self.x_density = binaryIO.readU16(self.img)
                self.y_density = binaryIO.readU16(self.img)
                length_counter += 4

                self.x_thumb = binaryIO.readU8(self.img)
                self.y_thumb = binaryIO.readU8(self.img)
                length_counter += 2

                self.thumbnail_RGB = []
                for i in range(length_counter, APP0_length, 3):
                    red = binaryIO.readU8(self.img)
                    green = binaryIO.readU8(self.img)
                    blue = binaryIO.readU8(self.img)
                    self.thumbnail_RGB.append((red, green, blue))

                # note the length won't increment the last time, even though it reads three bytes
                length_counter += 3 if (self.thumbnail_RGB.__len__() > 0) else 0

                # make sure the thumbnail_RGB is as long as we expect
                # it should be (3 * x_thumb * y_thumb) bytes, or x_thumb * y_thumb RGB pixels
                success = self.thumbnail_RGB.__len__() == (self.x_thumb * self.y_thumb) and\
                    length_counter == APP0_length

                # if things went smoothly
                if success:
                    print("successfully read APP0 segment")
                else:
                    if (length_counter != APP0_length):
                        raise Exception("Section longer than indicated by APP0_length")
                    else:
                        print("Expected size:", self.x_thumb * self.y_thumb, "pixels")
                        print("Actual size:", self.thumbnail_RGB.__len__(), "pixels")
                        raise Exception("RGB image data was not the expected size")
            else:
                raise InvalidFormatError("Invalid format identifier in APP0; expected null-terminated 'J','F','I','F'")
        else:
            raise InvalidFormatError("APP0 marker invalid")
        return
