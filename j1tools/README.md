# J1 Tools

A collection of tools for working with the J1 Forth CPU.

These tools are a work in progress.  They are in development and
are not even in an alpha state.

## Installation

### For Development
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

# Install in development mode with dev dependencies
cd j1tools
pip install -e ".[dev]"
```

Note: For Windows PowerShell users, activate the virtual environment with:
```bash
.\venv\Scripts\Activate.ps1
```

### For Users
To install j1tools for normal use:
```bash
pip install j1tools
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
- Immediate values: #dec_value or #$hex_value
- Control flow: JMP, CALL, RET, 0BRANCH
- Labels for jump targets

Example assembly:
```bash
start:          ; Program start
    NOP         ; Do nothing
    DUP         ; Duplicate top of stack
    #$1234      ; Push hex value
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

### Running Tests

To run the test suite:
```bash
pytest tests/
```

For verbose output:
```bash
pytest tests/ -v
```

### Test Coverage

To check test coverage:
```bash
# Basic coverage report
pytest --cov=j1tools tests/

# Detailed coverage with missing lines
pytest --cov=j1tools --cov-report=term-missing tests/

# Generate HTML coverage report
pytest --cov=j1tools --cov-report=html tests/
```

The HTML report will be generated in the `htmlcov` directory. Open `htmlcov/index.html` in your browser for an interactive coverage report.

## References

For more details on the J1 instruction set and architecture, see:
- [doc/j1.pdf](../doc/j1.pdf) the original J1 paper.
- [doc/j1a-reference.pdf](../doc/j1a-reference.pdf) the J1a reference manual.
- [doc/assembly.md](../doc/assembly.md) for detailed assembly syntax
- [J1a SwapForth built with IceStorm](https://excamera.com/sphinx/article-j1a-swapforth.html)
- [SwapForth](https://github.com/jamesbowman/swapforth)

