import sys
import argparse


def hex_to_coe(hex_file):
    """Convert hex file to COE format and print to stdout"""
    # Read hex file, skip comments and empty lines
    with open(hex_file, "r") as f:
        hex_data = [
            line.split("//")[0].strip() for line in f
        ]  # Split on // and take first part
        hex_data = [line for line in hex_data if line]  # Remove empty lines

    # Output COE format
    print("memory_initialization_radix=16;")
    print("memory_initialization_vector=")
    # Print all values except the last one with commas
    for value in hex_data[:-1]:
        print(f"{value},")
    # Print the last value with semicolon
    print(f"{hex_data[-1]};")


def hex_to_mif(hex_file):
    """Convert hex file to MIF format and print to stdout"""
    # Read hex file, skip comments and empty lines
    with open(hex_file, "r") as f:
        hex_data = [
            line.split("//")[0].strip() for line in f
        ]  # Split on // and take first part
        hex_data = [line for line in hex_data if line]  # Remove empty lines

    # Output MIF format - each line is a 16-bit binary number
    for value in hex_data:
        binary = format(int(value, 16), "016b")
        print(binary)


def main():
    parser = argparse.ArgumentParser(
        description="Convert hex file to COE or MIF format"
    )
    parser.add_argument("hex_file", help="Input hex file")
    args = parser.parse_args()

    # Determine format based on command name
    if sys.argv[0].endswith("hex2coe"):
        hex_to_coe(args.hex_file)
    else:
        hex_to_mif(args.hex_file)


if __name__ == "__main__":
    main()
