# J1 Tools Utilities

This directory contains utility scripts for the J1 Tools package.

## Available Utilities

- **gen_ebnf** - Generates EBNF (Extended Backus-Naur Form) from Lark grammar files in either W3C or RR-compatible format
- **rebuild_make** - Recursively finds directories with Makefiles and executes make commands to rebuild projects

## Installation for Development

For development work on the utilities, install j1tools in development mode:

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

## gen_ebnf

The `gen_ebnf` utility converts Lark grammar files to EBNF (Extended Backus-Naur Form) syntax. It can output in two formats:
1. W3C-style EBNF - Standard format used by W3C specifications
2. RR-compatible EBNF - Format compatible with the RR - Railroad Diagram Generator

This is particularly useful for generating documentation and visualizations of the J1 syntax.

### Usage

After installing the j1tools package, the script is available as a command-line tool:

```bash
# Basic usage to convert a Lark grammar to RR-compatible EBNF
gen_ebnf path/to/grammar.lark

# Output to a file
gen_ebnf path/to/grammar.lark -o output.ebnf

# Generate W3C-style EBNF
gen_ebnf path/to/grammar.lark --format w3c
```

### Options

- `input_file` - Path to the Lark grammar file
- `-o`, `--output` - Output file (default: stdout)
- `--format` - Output format: rr (Railroad) or w3c (W3C EBNF) (default: rr)

### Examples

Generate RR-compatible EBNF from the J1 grammar:

```bash
gen_ebnf j1tools/j1tools/assembler/j1.lark > j1_rr_grammar.ebnf
```

Generate W3C-style EBNF and save to a file:

```bash
gen_ebnf j1tools/j1tools/assembler/j1.lark --format w3c -o j1_w3c_grammar.ebnf
```

### Running as a Script

You can also run the script directly:

```bash
python -m j1tools.utils.gen_ebnf
# or
python j1tools/j1tools/utils/gen_ebnf.py j1tools/j1tools/assembler/j1.lark
```

## rebuild_make

The `rebuild_make` utility recursively finds directories with Makefiles and runs `make cleanall` followed by `make` in each one. This is useful for rebuilding test cases or firmware after making changes to the grammar, assembler, or source files.

### Installation

After installing the j1tools package, the script is available as a command-line tool:

```bash
# Install the j1tools package in development mode
pip install -e .

# Now you can use the rebuild_make command from anywhere
rebuild_make
```

### Usage

```bash
rebuild_make [options]
```

### Options

- `--verbose, -v` - Show verbose output from make commands
- `--filter, -f STR` - Only rebuild directories matching this substring
- `--dry-run, -n` - Don't run commands, just show what would be done
- `--directory, -d DIR` - Start searching from this directory (default: current directory)
- `--help, -h` - Show help message and exit

### Examples

Rebuild all Makefiles in the current directory and subdirectories:

```bash
rebuild_make
```

Rebuild directories matching a pattern:

```bash
rebuild_make --filter control
```

Show what would be rebuilt without actually running any commands:

```bash
rebuild_make --dry-run
```

Rebuild from a specific directory:

```bash
rebuild_make --directory path/to/tests
```

Show help message:

```bash
rebuild_make --help
```

### Running as a Script

You can also run the script directly from the utils directory:

```bash
python -m j1tools.utils.rebuild_make
# or
python j1tools/utils/rebuild_make.py
```