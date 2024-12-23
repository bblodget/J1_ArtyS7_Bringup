import sys
import argparse


def hex_to_coe(hex_file, coe_file):
    # Read hex file, skip comments and empty lines
    with open(hex_file, "r") as f:
        hex_data = [
            line.split("//")[0].strip() for line in f
        ]  # Split on // and take first part
        hex_data = [line for line in hex_data if line]  # Remove empty lines

    # Write COE file
    with open(coe_file, "w") as f:
        f.write("memory_initialization_radix=16;\n")
        f.write("memory_initialization_vector=\n")
        # Write all values except the last one with commas
        for value in hex_data[:-1]:
            f.write(f"{value},\n")
        # Write the last value with semicolon
        f.write(f"{hex_data[-1]};")


def hex_to_mif(hex_file, mif_file):
    # Read hex file, skip comments and empty lines
    with open(hex_file, "r") as f:
        hex_data = [
            line.split("//")[0].strip() for line in f
        ]  # Split on // and take first part
        hex_data = [line for line in hex_data if line]  # Remove empty lines

    # Write MIF file
    with open(mif_file, "w") as f:
        # Convert each hex value to 16-bit binary string
        for value in hex_data:
            binary = format(int(value, 16), "016b")
            f.write(f"{binary}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Convert hex file to COE or MIF format"
    )
    parser.add_argument("hex_file", help="Input hex file")
    parser.add_argument("output_file", help="Output file (COE or MIF)")
    parser.add_argument(
        "--format",
        choices=["coe", "mif"],
        default="coe",
        help="Output format (default: coe)",
    )
    args = parser.parse_args()

    if args.format == "coe":
        hex_to_coe(args.hex_file, args.output_file)
    else:
        hex_to_mif(args.hex_file, args.output_file)


if __name__ == "__main__":
    main()
