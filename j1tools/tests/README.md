# J1 Assembler Test Suite

This directory contains the tests for the J1 Assembler and related tools.

## Test Files

The `test_files` directory contains various test cases organized by feature area:

- `arith/` - Arithmetic operations tests
- `control/` - Control flow tests (if/then, loops, etc.)
- `include/` - Testing the include directive
- `io_lib/` - Testing I/O operations
- `macros/` - Testing macro functionality
- `memory/` - Testing memory operations

## Rebuilding Tests

After making changes to the grammar, assembler, or test files, you can use the `rebuild_tests.py` script to update all the test outputs:

```bash
./rebuild_tests.py
```

This will run `make cleanall` followed by `make` in each test directory to rebuild all the test outputs.

### Options

The script has several options:

- `--verbose, -v` - Show verbose output from make commands
- `--filter, -f STR` - Only rebuild tests matching this substring
- `--dry-run, -n` - Don't run commands, just show what would be done

### Examples

Rebuild a specific test:

```bash
./rebuild_tests.py --filter control/if_then
```

Show what would be rebuilt without actually running the commands:

```bash
./rebuild_tests.py --dry-run
```

Run with verbose output:

```bash
./rebuild_tests.py --verbose
```

## Running Tests

The main test suite can be run with:

```bash
python -m unittest discover
```

Or:

```bash
python -m j1tools.tests.test_assembler
``` 