# J1 Tools Utilities

This directory contains utility scripts for the J1 Tools package.

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