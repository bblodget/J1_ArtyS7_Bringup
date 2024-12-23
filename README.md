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

### Build Steps

1. Create block RAM IP using Block Memory Generator
   - Configure as True Dual Port RAM
   - 16KB depth
   - 16-bit width
   - Load initialization file (.coe format)

2. Build Vivado Project
   - Add source files
   - Generate bitstream
   - Program device

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
