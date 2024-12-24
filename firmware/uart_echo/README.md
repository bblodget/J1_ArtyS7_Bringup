# UART Echo Example

This directory contains a simple UART echo program for the J1 processor implemented in assembly language. It serves as both a basic test of the UART functionality and an example of using the j1asm toolchain.

## Program Description

The program continuously monitors the UART receive line. When a character is received, it:
1. Checks if there's valid data available
2. Reads the character from the UART RX
3. Waits until the UART TX is not busy
4. Echoes the character back through UART TX

## Memory Map

- `0x4000`: UART RX Data Register
- `0x4001`: UART TX Data Register
- `0x4002`: UART Valid Status Register
- `0x4003`: UART Busy Status Register

## Prerequisites

Before building, ensure you have the j1tools installed and configured. See [j1tools/README.md](../../j1tools/README.md) for setup instructions.

## Building

To build and program the FPGA:

```bash
make        # Assembles the code and generates new bitstream
make program # Programs the FPGA with the new bitstream
```

## Development Notes

This example serves as a development vehicle for the j1asm assembler program. It demonstrates:
- Basic I/O operations
- Control flow using branches and jumps
- Subroutine calls
- Stack manipulation
