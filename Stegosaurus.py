"""Creates a small command-line tool to do stegranography using the algorithms in this program"""

import sys
import argparse
import re
import LSB
import jpeg
from PIL import Image

mode_help = "Required; 'hide' or 'show'; choose whether to hide or show a message in a file"
i_help = "Required; specify path to source image"
msg_s_help = "The message you wish to hide; can be text or a number"
msg_f_help = "The file you wish to hide"
o_help = "Path to which to save the steganographic image; if not specified, the input file will be overwritten"
algorithm_help = "Required; the algorithm you want to use; currently supported algorithms are:\n\t- LSB (least \
significant bit steganography)"

parser = argparse.ArgumentParser()
parser.add_argument("-mode", "--mode", help=mode_help, required=True)
parser.add_argument("-i", "--input-file", help=i_help, required=True)
parser.add_argument("-msg", "--message", help=msg_s_help, required=False)
parser.add_argument("-mf", "--message-file", help=msg_f_help, required=False)
parser.add_argument("-o", "--output-file", help=o_help, required=False)
parser.add_argument("-a", "--algorithm", help=algorithm_help, required=False)

args = parser.parse_args()

if not args.algorithm:
    print("No algorithm specified; assuming least-significant-bit method")
    algorithm = "LSB"   # assume LSB if no algorithm is specified
else:
    algorithm = str(args.algorithm)

# use a regex to see if the file is a bmp or png; this will allow us to catch incorrect file errors before PIL
if re.search(r"((.bmp)|(.png))$", str(args.input_file)):
    try:
        i_file = Image.open(str(args.input_file)).convert("RGBA")
        i_file.load()
    except FileNotFoundError:
        parser.error("System could not find the file specified")
        sys.exit(2)

    # Make sure we have a valid message
    if str(args.mode) == "hide":
        if args.message_file and args.message:
            parser.error("You cannot use both a message and a message file")
        elif not args.message_file and not args.message:
            parser.error("You must specify a message or message file")

    if args.output_file is not None:
        print("o_file specified")
        print("all output going to file")
        print()

        if str(args.mode) == "hide":
            try:
                o_file = Image.open(str(args.output_file)).convert("RGBA")
            except FileNotFoundError:
                print("System could not find the file specified; creating...")
                o_file = Image.new("RGBA", (i_file.width, i_file.height))

            if args.message and not args.message_file:
                print("Algorithm:", algorithm)
                if algorithm == "LSB":
                    o_file = LSB.hide_message(i_file, str(args.message))
                    o_file.save(str(args.output_file))
                else:
                    print("Invalid algorithm!")
            elif args.message_file and not args.message:
                try:
                    file = open(str(args.message_file), "rb")
                    content = file.read()
                    if algorithm == "LSB":
                        o_file = LSB.hide_message(i_file, content)
                        o_file.save(str(args.output_file))
                except FileNotFoundError:
                    print("**** System could not find the message file specified")

        elif str(args.mode) == "show":
            o_file = open(str(args.output_file), "wb")

            if algorithm == "LSB":
                message = LSB.reveal_message(i_file)
                if type(message) is str:
                    print("Steganographic data is not a bytearray; converting string to utf-8-encoded bytearray...")
                    print("Writing data to file...")
                    o_file.write(bytearray(message, "utf-8"))
                else:
                    print("Writing data to file...")
                    o_file.write(message)
                o_file.close()

    else:
        # Overwrite i_file
        print("no o_file specified;")
        print("printing output")
        print()

        if str(args.mode) == "hide":
            if args.message and not args.message_file:
                if algorithm == "LSB":
                    i_file = LSB.hide_message(i_file, str(args.message))
                    print("Updating input file...")
                    i_file.save(str(args.input_file))
            elif args.message_file and not args.message:
                try:
                    file = open(str(args.message_file), "rb")
                    content = file.read()
                    if algorithm == "LSB":
                        i_file = LSB.hide_message(i_file, content)
                        i_file.save(str(args.input_file))
                except FileNotFoundError:
                    print("**** System could not find the message file specified")

        elif str(args.mode) == "show":
            print("Message:")

            if algorithm == "LSB":
                message = LSB.reveal_message(i_file)
                print(message)
else:
    print("file is not a bitmap image; must be of type .png or .bmp")
