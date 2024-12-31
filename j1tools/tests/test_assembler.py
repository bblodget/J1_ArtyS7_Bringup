import pytest
from pathlib import Path
from j1tools.assembler.asm import J1Assembler
from lark.exceptions import VisitError


@pytest.fixture
def assembler():
    return J1Assembler(debug=False)


@pytest.fixture
def add_test_source():
    test_file = Path(__file__).parent.parent.parent / "firmware/add_test/add_test.asm"
    with open(test_file, "r") as f:
        return f.read()


def test_number_literals(assembler):
    # Test hex and decimal number handling
    hex_result = assembler.transform(assembler.parse("#$2A"))
    dec_result = assembler.transform(assembler.parse("#10"))

    assert hex_result[0] == 0x802A  # 0x8000 | 0x2A
    assert dec_result[0] == 0x800A  # 0x8000 | 10


@pytest.mark.parametrize(
    "source,expected",
    [
        ("T+N", 0x6200),
        ("T-N", 0x6C00),
        ("T&N", 0x6300),
        ("T|N", 0x6400),
        ("T^N", 0x6500),
        ("~T", 0x6600),
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


def test_add_test_program(assembler, add_test_source):
    result = assembler.transform(assembler.parse(add_test_source))

    # Expected instruction sequence for add_test.asm
    expected = [
        0x802A,  # Push 2A hex
        0x800A,  # Push 10 decimal
        0x4005,  # CALL add_nums (at address 5)
        0x6103,  # N[d-1] - N operation with d-1 modifier
        0x0009,  # JMP wait_forever (at address 9)
        0x6203,  # T+N[d-1]
        0x6024,  # T[T->R,r+1]
        0x600C,  # T[r-1]
        0x608C,  # T[RET,r-1]
        0x6000,  # T[d+0]
        0x0009,  # JMP wait_forever (at address 9)
    ]

    assert result == expected


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
        ("DUP", 0x6001),  # T    [d+1]
        ("DROP", 0x6103),  # N    [d-1]
        ("SWAP", 0x6110),  # N    [T->N]
        ("OVER", 0x6111),  # N    [T->N,d+1]
        ("NIP", 0x6003),  # T    [d-1]
        ("NOOP", 0x6000),  # T    []
    ],
)
def test_stack_words(assembler, source, expected):
    """Test that stack operation words generate the correct machine code."""
    result = assembler.transform(assembler.parse(source))
    assert (
        result[0] == expected
    ), f"Stack operation {source} should generate {expected:04x}, got {result[0]:04x}"
