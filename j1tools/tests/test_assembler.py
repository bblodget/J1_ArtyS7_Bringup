import pytest
from j1tools.assembler.asm import J1Assembler
from lark.exceptions import VisitError
from pathlib import Path
import logging


@pytest.fixture
def assembler(j1debug):
    return J1Assembler(debug=j1debug)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("T", 0x6000),  # Basic T
        ("N", 0x6100),  # Basic N
        ("T+N", 0x6200),  # Add
        ("T&N", 0x6300),  # AND
        ("T|N", 0x6400),  # OR
        ("T^N", 0x6500),  # XOR
        ("~T", 0x6600),  # NOT
        ("N==T", 0x6700),  # Equal
        ("N<T", 0x6800),  # Less than
        ("Nu<T", 0x6F00),  # Unsigned less than
    ],
)
def test_alu_operations(assembler, source, expected):
    """Test basic ALU operations without modifiers."""
    tree = assembler.parse(source)
    assembler.transform(tree)
    result = assembler.get_bytecodes()
    assert result[0] == expected


@pytest.mark.parametrize(
    "source,expected",
    [
        ("T[T->N]", 0x6010),  # Copy T to N
        ("T[T->R]", 0x6020),  # Copy T to R
        ("T[N->[T]]", 0x6030),  # Store to memory
        ("T[N->io[T]]", 0x6040),  # Store to IO
        ("T[IORD]", 0x6050),  # IO Read
        ("T[fDINT]", 0x6060),  # Disable interrupts
        ("T[fEINT]", 0x6070),  # Enable interrupts
        ("T[RET]", 0x6080),  # Return
    ],
)
def test_stack_effects(assembler, source, expected):
    """Test stack effect modifiers."""
    tree = assembler.parse(source)
    assembler.transform(tree)
    result = assembler.get_bytecodes()
    assert result[0] == expected


@pytest.mark.parametrize(
    "source,expected",
    [
        ("T[d+0]", 0x6000),  # Stack unchanged
        ("T[d+1]", 0x6001),  # Push
        ("T[d-1]", 0x6003),  # Pop
        ("T[d-2]", 0x6002),  # Pop two
        ("T[r+0]", 0x6000),  # R-stack unchanged
        ("T[r+1]", 0x6004),  # R-push
        ("T[r-1]", 0x600C),  # R-pop
        ("T[r-2]", 0x6008),  # R-pop two
    ],
)
def test_stack_deltas(assembler, source, expected):
    """Test stack delta modifiers."""
    tree = assembler.parse(source)
    assembler.transform(tree)
    result = assembler.get_bytecodes()
    assert result[0] == expected


def test_jump_instructions(assembler):
    """Test jump instructions with label resolution."""
    source = """
    : start
        JMP 'end
    : middle
        ZJMP 'start
    : end
        CALL 'middle
    """
    tree = assembler.parse(source)
    assembler.transform(tree)
    result = assembler.get_bytecodes()
    assert result[0] == 0x0002  # JMP to end (addr 2)
    assert result[1] == 0x2000  # ZJMP to start (addr 0)
    assert result[2] == 0x4001  # CALL to middle (addr 1)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("#42", 0x802A),  # Decimal
        ("#$2A", 0x802A),  # Hex (same as 42)
        ("#0", 0x8000),  # Zero
        ("#$FF", 0x80FF),  # Max 8-bit hex
        ("#255", 0x80FF),  # Max 8-bit decimal
    ],
)
def test_number_literals(assembler, source, expected):
    """Test number literal handling."""
    tree = assembler.parse(source)
    assembler.transform(tree)
    result = assembler.get_bytecodes()
    assert result[0] == expected


def test_invalid_syntax(assembler):
    """Test invalid syntax handling."""
    with pytest.raises(Exception):
        assembler.transform(assembler.parse("INVALID"))


def test_undefined_label(assembler):
    """Test undefined label handling."""
    with pytest.raises((ValueError, VisitError)) as exc_info:
        assembler.transform(assembler.parse("JMP undefined_label"))
    assert "Undefined label" in str(exc_info.value)


def test_duplicate_label(assembler):
    """Test duplicate label handling."""
    source = """
    : label T
    : label N
    """
    with pytest.raises((ValueError, VisitError)) as exc_info:
        assembler.transform(assembler.parse(source))
    assert "Duplicate label" in str(exc_info.value)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("T+N[T->N,d-1]", 0x6213),  # ALU with stack effect and delta
        ("T[T->R,r+1,d-1]", 0x6027),  # Multiple modifiers
        ("N[RET,d-1,r-1]", 0x618F),  # Return with stack effects
        ("T[N->[T],d-2]", 0x6032),  # Memory store with stack delta
    ],
)
def test_combined_modifiers(assembler, source, expected):
    """Test combinations of modifiers."""
    tree = assembler.parse(source)
    assembler.transform(tree)
    result = assembler.get_bytecodes()
    assert result[0] == expected


##############################
# The programs in the firmware directory
##############################


@pytest.mark.parametrize(
    "category,test_name",
    [
        ("memory", "basic_memory"),
        ("memory", "memory_init"),  # Add our new memory initialization test
        ("arith", "basic_ops"),
        ("arith", "add_subroutine"),
        ("include", "basic_include"),
        ("include", "nested_include"),
        ("macros", "macros_basic"),
        ("macros", "macros_words"),
        ("macros", "base_alu"),
        ("macros", "base_compare"),
        ("macros", "base_dup_over"),
        ("macros", "base_elided"),
        ("macros", "base_io"),
        ("macros", "base_rstack"),
        ("macros", "base_status"),
        ("io_lib", "io_org"),
        ("io_lib", "io_words"),
        ("control", "if_then"),
        ("control", "nested_if_then"),
        ("control", "if_else_then"),
        ("control", "loop_until"),
        ("control", "nested_loop_until"),
        ("control", "loop_while"),
        ("control", "do_loop"),
        ("control", "raw_nested_do_loop"),
        ("control", "nested_do_loop"),
        ("control", "warn_ijk"),
        ("control", "do_plus_loop"),
        ("control", "do_neg_loop"),
        ("control", "raw_loop"),
        ("control", "raw_i_loop"),
        ("control", "do_i_loop"),
        # ("constants", "constants_basic"),
        ("variables", "table"),
        ("variables", "chars"),
        ("firmware", "blinky"),
        ("firmware", "count"),
        ("firmware", "fetch"),
        ("firmware", "interrupt_test"),
    ],
)
def test_program(assembler, category, test_name):
    """Generic test runner for assembly programs."""
    # Construct path to test files
    if category == "firmware":
        base_path = Path(__file__).parent.parent.parent / "firmware" / test_name
    else:
        base_path = Path(__file__).parent / "test_files" / category / test_name
    asm_file = base_path / f"{test_name}.asm"
    hex_file = base_path / f"{test_name}.hex"

    # Read source and expected output
    with open(asm_file, "r") as f:
        source = f.read()
    with open(hex_file, "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]

    # Process the file
    tree = assembler.parse(source, str(asm_file))
    assembler.transform(tree)
    result = assembler.get_bytecodes()

    # Compare results with detailed error message
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )


# Special case for basic_include since it needs the words.asm file
@pytest.fixture
def basic_include_files(tmp_path):
    """Setup for basic include test that requires additional files."""
    test_dir = tmp_path / "basic_include"
    test_dir.mkdir()

    # Copy files from test_files directory
    base_path = Path(__file__).parent / "test_files/include/basic_include"

    # Copy words.asm to test directory
    words_path = base_path / "words.asm"
    with open(words_path, "r") as f:
        words_content = f.read()
    with open(test_dir / "words.asm", "w") as f:
        f.write(words_content)

    # Get main test file
    filename = "basic_include.asm"
    with open(base_path / filename, "r") as f:
        source = f.read()

    # Get expected output
    with open(base_path / "basic_include.hex", "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]

    return str(test_dir / filename), source, expected


def test_basic_include_program(assembler, basic_include_files, tmp_path):
    """Special test case for basic include functionality."""
    filename, source, expected = basic_include_files

    # Write the main test file
    with open(filename, "w") as f:
        f.write(source)

    # Process the file
    tree = assembler.parse(source, filename)
    assembler.transform(tree)
    result = assembler.get_bytecodes()

    assert result == expected


def test_loop_index_warnings(tmp_path, caplog):
    """Test warnings for i, j, k loop index words."""
    # Setup assembler with debug OFF
    assembler = J1Assembler(debug=False)
    
    # Get the test files
    base_path = Path(__file__).parent / "test_files/control/warn_ijk"
    asm_file = base_path / "warn_ijk.asm"
    build_file = base_path / "warn_ijk.build"
    
    # Read source and expected build output
    with open(asm_file, "r") as f:
        source = f.read()
    with open(build_file, "r") as f:
        # Only get WARNING lines from build file
        expected_warnings = [
            line.strip().replace("WARNING: ", "") 
            for line in f 
            if line.strip() and line.startswith("WARNING")
        ]
    
    # Set logging level to WARNING to capture only warnings
    caplog.set_level(logging.WARNING)
    
    # Process the file and capture log output
    tree = assembler.parse(source, str(asm_file))
    assembler.transform(tree)
    
    # Get actual warnings from caplog, strip full path to match expected
    actual_warnings = [
        record.message.split(str(base_path) + "/")[-1] 
        for record in caplog.records
        if record.levelname == "WARNING"
    ]
    
    # Compare warnings
    assert len(actual_warnings) == len(expected_warnings), \
        f"Expected {len(expected_warnings)} warnings, got {len(actual_warnings)}"
    
    for expected, actual in zip(expected_warnings, actual_warnings):
        assert expected == actual, \
            f"Expected warning '{expected}' not found in '{actual}'"
