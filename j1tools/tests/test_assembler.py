import pytest
from pathlib import Path
from j1tools.assembler.asm import J1Assembler
from lark.exceptions import VisitError


@pytest.fixture
def assembler():
    return J1Assembler(debug=False)


@pytest.fixture
def add_test_files():
    base_path = (
        Path(__file__).parent.parent.parent / "firmware/low_level_add_subroutine"
    )
    with open(base_path / "low_level_add_subroutine.asm", "r") as f:
        source = f.read()
    with open(base_path / "low_level_add_subroutine.hex", "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]
    return source, expected


@pytest.fixture
def stack_test_files():
    base_path = Path(__file__).parent.parent.parent / "firmware/stack_test"
    with open(base_path / "stack_test.asm", "r") as f:
        source = f.read()
    with open(base_path / "stack_test.hex", "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]
    return source, expected


@pytest.fixture
def arith_test_files():
    base_path = Path(__file__).parent.parent.parent / "firmware/arith_test"
    with open(base_path / "arith_test.asm", "r") as f:
        source = f.read()
    with open(base_path / "arith_test.hex", "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]
    return source, expected


@pytest.fixture
def arith_ret_test_files():
    base_path = Path(__file__).parent.parent.parent / "firmware/arith_ret_test"
    with open(base_path / "arith_ret_test.asm", "r") as f:
        source = f.read()
    with open(base_path / "arith_ret_test.hex", "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]
    return source, expected


@pytest.fixture
def comparison_test_files(request):
    """Load the comparison test assembly and hex files."""
    return load_test_files("comparison_test")


@pytest.fixture
def comparison_ret_test_files():
    """Load the comparison ret test assembly and hex files."""
    return load_test_files("comparison_ret_test")


def test_number_literals(assembler):
    # Test hex and decimal number handling
    hex_result = assembler.transform(assembler.parse("#$2A"))
    dec_result = assembler.transform(assembler.parse("#10"))

    assert hex_result[0] == 0x802A  # 0x8000 | 0x2A
    assert dec_result[0] == 0x800A  # 0x8000 | 10


@pytest.mark.parametrize(
    "source,expected",
    [
        ("~T", 0x6600),
        ("T+N", 0x6200),
        ("N-T", 0x6C00),
        ("T&N", 0x6300),
        ("T|N", 0x6400),
        ("T^N", 0x6500),
    ],
)
def test_alu_operations(assembler, source, expected):
    tree = assembler.parse(source)
    result = assembler.transform(tree)
    assert result[0] == expected


@pytest.mark.parametrize(
    "source,expected",
    [
        ("T[d+1]", 0x6001),
        ("T[d-1]", 0x6003),
        ("T[r+1]", 0x6004),
        ("T[r-1]", 0x600C),
    ],
)
def test_stack_modifiers(assembler, source, expected):
    result = assembler.transform(assembler.parse(source))
    assert result[0] == expected


def test_jump_instructions(assembler):
    source = """
    start:
        JMP end
    middle:
        ZJMP start
    end:
        CALL middle
    """
    result = assembler.transform(assembler.parse(source))

    # Check that jumps resolve to correct addresses
    assert result[0] == 0x0002  # JMP to end (addr 2)
    assert result[1] == 0x2000  # ZJMP to start (addr 0)
    assert result[2] == 0x4001  # CALL to middle (addr 1)


def test_add_test_program(assembler, add_test_files):
    source, expected = add_test_files
    result = assembler.transform(assembler.parse(source))
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )


def test_invalid_syntax(assembler):
    with pytest.raises(Exception):
        assembler.transform(assembler.parse("INVALID"))


def test_undefined_label(assembler):
    with pytest.raises((ValueError, VisitError)) as exc_info:
        assembler.transform(assembler.parse("JMP undefined_label"))
    # Verify the error message regardless of exception type
    assert "Undefined label" in str(exc_info.value)


def test_duplicate_label(assembler):
    source = """
    label: T
    label: N
    """
    with pytest.raises((ValueError, VisitError)) as exc_info:
        assembler.transform(assembler.parse(source))
    # Verify the error message regardless of exception type
    assert "Duplicate label" in str(exc_info.value)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("DUP", 0x6011),  # T    [T->N,d+1]         # Was 0x6001
        ("DROP", 0x6103),  # N    [d-1]              # Unchanged
        ("SWAP", 0x6110),  # N    [T->N]             # Unchanged
        ("OVER", 0x6111),  # N    [T->N,d+1]         # Unchanged
        ("NIP", 0x6003),  # T    [d-1]              # Unchanged
        ("NOOP", 0x6000),  # T    []                 # Unchanged
        (">R", 0x6027),  # T    [T->R,r+1,d-1]     # Was 0x6127
        ("R>", 0x6B1D),  # rT   [T->N,r-1,d+1]     # Unchanged
        ("R@", 0x6B11),  # rT   [T->N,d+1]         # Unchanged
    ],
)
def test_stack_words(assembler, source, expected):
    """Test that stack operation words generate the correct machine code."""
    result = assembler.transform(assembler.parse(source))
    assert (
        result[0] == expected
    ), f"Stack operation {source} should generate {expected:04x}, got {result[0]:04x}"


def test_stack_test_program(assembler, stack_test_files):
    source, expected = stack_test_files
    result = assembler.transform(assembler.parse(source))
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )


@pytest.mark.parametrize(
    "source,expected",
    [
        ("T+N", 0x6200),  # Add
        ("N-T", 0x6C00),  # Subtract
        ("1+", 0x7600),  # Increment (0x1600 with ALU base)
        ("1-", 0x7700),  # Decrement (0x1700 with ALU base)
        ("2*", 0x6A00),  # Double (0x0A00 with ALU base)
        ("2/", 0x6900),  # Half (0x0900 with ALU base)
    ],
)
def test_arithmetic_operations(assembler, source, expected):
    """Test that arithmetic operations generate the correct machine code."""
    result = assembler.transform(assembler.parse(source))
    assert (
        result[0] == expected
    ), f"Arithmetic operation {source} should generate {expected:04x}, got {result[0]:04x}"


def test_arith_test_program(assembler, arith_test_files):
    source, expected = arith_test_files
    result = assembler.transform(assembler.parse(source))
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )


def test_arith_ret_test_program(assembler, arith_ret_test_files):
    source, expected = arith_ret_test_files
    result = assembler.transform(assembler.parse(source))
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )


def test_comparison_test_program(assembler, comparison_test_files):
    """Test that comparison operations generate the correct machine code."""
    source, expected = comparison_test_files
    result = assembler.transform(assembler.parse(source))
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )


def test_comparison_ret_test_program(assembler, comparison_ret_test_files):
    """Test that comparison operations with RET generate the correct machine code."""
    source, expected = comparison_ret_test_files
    result = assembler.transform(assembler.parse(source))
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )


def load_test_files(test_name):
    """Helper function to load .asm and .hex files for a test.

    Args:
        test_name: Name of the test (e.g., 'add_test', 'stack_test')

    Returns:
        tuple: (source_code, expected_hex_values)

    Raises:
        FileNotFoundError: If either .asm or .hex file is missing
    """
    base_path = Path(__file__).parent.parent.parent / f"firmware/{test_name}"
    asm_path = base_path / f"{test_name}.asm"
    hex_path = base_path / f"{test_name}.hex"

    if not asm_path.exists():
        raise FileNotFoundError(f"Assembly file not found: {asm_path}")
    if not hex_path.exists():
        raise FileNotFoundError(f"Hex file not found: {hex_path}")

    with open(asm_path, "r") as f:
        source = f.read()
    with open(hex_path, "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]

    return source, expected


@pytest.mark.parametrize(
    "source,expected",
    [
        ("T+N[d-1]", 0x6203),  # Add and drop
        ("T[d+0]", 0x6000),  # No effect
        ("T[T->R,r+1]", 0x6024),  # Push to return stack
        ("T[r-1]", 0x600C),  # Pop from return stack
        ("T[RET,r-1]", 0x608C),  # Return
        ("N[d-1]", 0x6103),  # Drop from data stack
        ("N-T[d-1]", 0x6C03),  # Subtract and drop
        ("T&N[d-1]", 0x6303),  # AND and drop
        ("T|N[d-1]", 0x6403),  # OR and drop
        ("T^N[d-1]", 0x6503),  # XOR and drop
        ("~T[d-1]", 0x6603),  # Invert and drop
    ],
)
def test_alu_modifiers(assembler, source, expected):
    """Test that ALU operations with modifiers generate the correct machine code."""
    result = assembler.transform(assembler.parse(source))
    assert (
        result[0] == expected
    ), f"ALU operation {source} should generate {expected:04x}, got {result[0]:04x}"


def test_multiple_alu_instructions(assembler):
    """Test that multiple ALU operations in sequence work correctly."""
    source = """
        #$2A                ; Push hex 2A (decimal 42)
        #10                 ; Push decimal 10
        T+N[d-1]            ; Add and drop
        #10                 ; Push decimal 10
    start:
        T+N[d-1]            ; Add and drop
        T[T->R,r+1]         ; Push to return stack
        T[r-1]              ; Pop from return stack
        T[RET,r-1]          ; Return
    """
    result = assembler.transform(assembler.parse(source))
    expected = [
        0x802A,  # Push hex 2A
        0x800A,  # Push decimal 10
        0x6203,  # T+N[d-1]
        0x800A,  # Push decimal 10
        0x6203,  # T+N[d-1]
        0x6024,  # T[T->R,r+1]
        0x600C,  # T[r-1]
        0x608C,  # T[RET,r-1]
    ]
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )


@pytest.mark.parametrize(
    "source,expected",
    [
        ("ADD+RET", 0x628F),  # ADD with RET
        ("++RET", 0x628F),  # Alternative ADD with RET
        ("-+RET", 0x6C8F),  # Subtract with RET
        ("SUBTRACT+RET", 0x6C8F),  # Alternative subtract with RET
        ("1++RET", 0x768C),  # Increment with RET
        ("1-+RET", 0x778C),  # Decrement with RET
        ("2*+RET", 0x6A8C),  # Double with RET
        ("2/+RET", 0x698C),  # Half with RET
        ("AND+RET", 0x638F),  # AND with RET
        ("OR+RET", 0x648F),  # OR with RET
        ("XOR+RET", 0x658F),  # XOR with RET
        ("INVERT+RET", 0x668C),  # INVERT with RET
    ],
)
def test_arith_ret_operations(assembler, source, expected):
    """Test that arithmetic operations with RET generate the correct machine code."""
    result = assembler.transform(assembler.parse(source))
    assert (
        result[0] == expected
    ), f"Operation {source} should generate {expected:04x}, got {result[0]:04x}"
