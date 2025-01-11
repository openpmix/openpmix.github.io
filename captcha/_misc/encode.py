#!/usr/bin/env python3
# Script to base64 encode the contents of a file.
# The script can also decode the encoded data if needed.
#
# NOTE: The base64 encoded data is typically the contents of
#       the meeting links so that the file committed to the repository
#       and posted online is obfuscated to avoid online browsing.
#
import base64
import sys
import argparse

decode=0
filename=""
script_name = "encode.py"

def read_file(file_path):
    content = ""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except Exception as e:
        print(f"Error: Unexpected error occurred: {e}", file=sys.stderr)

    return(content)

def main():
    p = argparse.ArgumentParser(description="Encode/decode datafile")

    p.add_argument(
        "filename",
        metavar="FILE",
        type=str,
        help="Path to input file to read."
    )
    p.add_argument(
        "-d", "--decode",
        action="store_true",
        help="Decode data"
    )

    args = p.parse_args()

    if len(sys.argv) < 2:
        print(f"Usage: {script_name} FILE", file=sys.stderr)
        return(1)

    data = read_file(args.filename)

    if args.decode:
        decoded_data = base64.b64decode(data).decode("utf-8")
        print(decoded_data)
    else:
        encoded_data = base64.b64encode(data.encode("utf-8")).decode("utf-8")
        print(encoded_data)

    return(0)

if __name__ == "__main__":
    retval = 0
    retval = main()
    sys.exit(retval)
