import pytest
from j1tools.assembler.asm import J1Assembler
from lark.exceptions import VisitError
from pathlib import Path


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
    result = assembler.transform(tree)
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
    result = assembler.transform(assembler.parse(source))
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
    result = assembler.transform(assembler.parse(source))
    assert result[0] == expected


def test_jump_instructions(assembler):
    """Test jump instructions with label resolution."""
    source = """
    start:
        JMP end
    middle:
        ZJMP start
    end:
        CALL middle
    """
    result = assembler.transform(assembler.parse(source))
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
    result = assembler.transform(assembler.parse(source))
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
    label: T
    label: N
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
    result = assembler.transform(assembler.parse(source))
    assert result[0] == expected


##############################
# The programs in the firmware directory
##############################


@pytest.fixture
def add_subroutine_files():
    base_path = Path(__file__).parent.parent.parent / "firmware/test_add_subroutine"
    filename = "test_add_subroutine.asm"
    with open(base_path / filename, "r") as f:
        source = f.read()
    with open(base_path / "test_add_subroutine.hex", "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]
    return filename, source, expected


def test_add_subroutine_program(assembler, add_subroutine_files):
    filename, source, expected = add_subroutine_files
    result = assembler.transform(assembler.parse(source, filename))
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )


@pytest.fixture
def basic_ops_files():
    base_path = Path(__file__).parent.parent.parent / "firmware/test_basic_ops"
    filename = "test_basic_ops.asm"
    with open(base_path / filename, "r") as f:
        source = f.read()
    with open(base_path / "test_basic_ops.hex", "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]
    return filename, source, expected


def test_basic_ops_program(assembler, basic_ops_files):
    filename, source, expected = basic_ops_files
    result = assembler.transform(assembler.parse(source, filename))
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )

@pytest.fixture
def macros_basic_files():
    base_path = Path(__file__).parent.parent.parent / "firmware/test_macros_basic"
    filename = "test_macros_basic.asm"
    with open(base_path / filename, "r") as f:
        source = f.read()
    with open(base_path / "test_macros_basic.hex", "r") as f:
        expected = [int(line.strip(), 16) for line in f if line.strip()]
    return filename, source, expected


def test_macros_basic_program(assembler, macros_basic_files):
    filename, source, expected = macros_basic_files
    result = assembler.transform(assembler.parse(source, filename))
    assert result == expected, "\n".join(
        f"Instruction {i}: expected {exp:04x}, got {act:04x}"
        for i, (exp, act) in enumerate(zip(expected, result))
        if exp != act
    )
