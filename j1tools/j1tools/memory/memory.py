import sys
import argparse


def hex_to_coe(hex_file):
    """Convert hex file to COE format and print to stdout"""
    # Read hex file, skip comments and empty lines
    with open(hex_file, "r") as f:
        hex_data = [line.split("//")[0].strip() for line in f]  # Split on // and take first part
        hex_data = [line for line in hex_data if line]  # Remove empty lines

    # Validate each hex value explicitly
    valid_chars = set("0123456789abcdefABCDEF")
    for hex_str in hex_data:
        # If any character in the hex_str is not in valid_chars, raise error
        if not all(c in valid_chars for c in hex_str):
            raise ValueError(f"Invalid hexadecimal value: {hex_str}")
        # Also attempt conversion to ensure it's a proper hex value
        int(hex_str, 16)

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


def mif_to_mem(mif_file):
    """Convert MIF format (binary) to MEM format and print to stdout"""
    with open(mif_file, "r") as f:
        binary_data = [line.strip() for line in f if line.strip()]

    # Convert each binary line to hex in MEM format
    for addr, binary in enumerate(binary_data):
        hex_value = format(int(binary, 2), "04X")
        print(f"@{addr:04X} {hex_value}")


def main():
    parser = argparse.ArgumentParser(description="Convert between memory file formats")
    parser.add_argument("input_file", help="Input file")
    args = parser.parse_args()

    # Determine format based on command name
    if sys.argv[0].endswith("hex2coe"):
        hex_to_coe(args.input_file)
    elif sys.argv[0].endswith("hex2mif"):
        hex_to_mif(args.input_file)
    elif sys.argv[0].endswith("mif2mem"):
        mif_to_mem(args.input_file)


if __name__ == "__main__":
    main()
