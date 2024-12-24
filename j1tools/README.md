# J1 Tools

A collection of tools for working with the J1 Forth CPU.

## Installation

I like to create a python virtual environment at the top
level of this project. Note, the venv directory is ignored
by the .gitignore file.

```bash
# Clone the repository
git clone https://github.com/bblodget/J1_ArtyS7_Bringup.git
cd J1_ArtyS7_Bringup

# Create the virtual environment
python -m venv venv

# Activate the virtual environment
source venv/Scripts/activate  # For Windows
source venv/bin/activate     # For Linux/MacOS
```

Then install the package in editable mode.

```bash
cd j1tools
pip install -e .
```

Note: For Windows PowerShell users, activate the virtual environment with:
```bash
.\venv\Scripts\Activate.ps1
```

## Tools Included

### J1 Assembler (j1asm)
Assembles J1 assembly code into hex format. Supports basic J1 instructions and label-based jumps.

```bash
j1asm input.asm > output.hex
```

Supported instructions:
- Basic operations: NOP, DUP, DROP
- Stack operations: OVER, SWAP
- I/O operations: IO@, IO!
- Immediate values: LIT #value
- Control flow: JMP, CALL, RET, 0BRANCH
- Labels for jump targets

Example assembly:
```bash
start:          ; Program start
    NOP         ; Do nothing
    DUP         ; Duplicate top of stack
    LIT #1234   ; Push value
    IO@         ; Read from IO
loop:
    JMP loop    ; Infinite loop
```

### Memory Format Converters
Tools for converting hex files to various memory initialization formats.

```bash
# Generate COE file (Vivado coefficient format)
hex2coe input.hex > output.coe

# Generate MIF file (Memory initialization format)
hex2mif input.hex > output.mif
```

Features:
- Preserves comments from source hex file
- Automatically handles empty lines
- COE format suitable for Vivado IP integration
- MIF format compatible with other tools

## Development

To run tests:

```bash
python -m pytest tests/
```

## References

For more details on the J1 instruction set and architecture, see:
- [J1 Forth Processor](https://excamera.com/sphinx/fpga-j1.html)
- [doc/assembly.md](doc/assembly.md) for detailed assembly syntax

