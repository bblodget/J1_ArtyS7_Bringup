# J1 Forth Processor on Spartan-7

This repository is a test area for porting the J1 Forth processor and Mecrisp-Ice Forth system to an AMD/Xilinx Spartan-7 FPGA using Vivado tools. 

## Features

- J1 Forth processor implementation for Spartan-7
- Mecrisp-Ice Forth system running at 12MHz
- UART communication (115200 baud)
- Memory-mapped I/O compatible with original Mecrisp-Ice
- 16KB dual-port block RAM implementation
- LED output display from processor stack

## Memory Map

The system uses the following memory-mapped I/O addresses:

- 0x1000: UART RX/TX
- 0x2000: UART Status (valid/busy bits)
- 0x4000: Ticks Counter/Control
- 0x8000: Cycles Counter

## Building

This project requires:
- Vivado 2024.1 or later
- Python 3.x for assembler tools
- Digilent Arty S7-50 board
- GNU Make
- Mecrisp-ICE Cross Compiler

### Build Steps

1. Generate Hex File
   There are two ways to generate the hex file:
   
   a. Using Mecrisp-Ice Cross Compiler (Recommended)
   - Follow the Mecrisp-Ice installation instructions
   - See `verilator-16bit-dualport/compilenucleus` for an example compilation script
   - This will generate a complete Forth system hex file
   
   b. Using J1 Assembler (Work in Progress)
   - Use the provided `asm.py` script to compile J1 assembly
   - Note: This is still under development and probably won't work.

2. Generate Memory Initialization File
   - Use the provided Python tools to convert your hex file to MIF format
   - Copy the generated file (e.g., `build/iceimage.mif`) to `ip_repo/j1_memory/j1_memory.mif`

3. Create and Build Vivado Projects
   ```bash
   cd vivado
   # Create memory editing project (optional)
   make memory
   
   # Create implementation project
   make top
   ```

4. Program the Device
   - Open Vivado
   - Connect to the Arty S7-50 board
   - Program the device with the generated bitstream

### Cleaning Build Files

```bash
cd vivado
make clean
```

This will remove all generated Vivado project files and logs.

## Tools

- J1 Assembler (Python) - Work in progress
- Hex to COE converter for Vivado memory initialization
- Hex to MIF converter for other tools

## References

- [Mecrisp-Ice Documentation](https://mecrisp-ice.readthedocs.io/en/latest/index.html)
- [Mecrisp-Ice Installation](https://mecrisp-ice.readthedocs.io/en/latest/usage.html)
- [Mecrisp-Ice Github old](https://github.com/zuloloxi/mecrisp-ice)
- [Mecrisp](https://mecrisp.sourceforge.net/)
- [J1 Forth Processor](https://excamera.com/sphinx/fpga-j1.html)
- [J1a SwapForth built with IceStorm](https://excamera.com/sphinx/article-j1a-swapforth.html)
- [SwapForth](https://github.com/jamesbowman/swapforth)
- [Arty-S7 Official Product Page](https://digilent.com/shop/arty-s7-spartan-7-fpga-development-board/)
- [Arty-S7 Reference Manual](https://digilent.com/reference/programmable-logic/arty-s7/reference-manual)
- [Arty-S7 Resource Center](https://digilent.com/reference/programmable-logic/arty-s7/start)
