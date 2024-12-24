import pytest
from io import StringIO
import sys
from j1tools.memory.memory import hex_to_coe, hex_to_mif

# Test data
TEST_HEX_DATA = """
6000        // NOP
6011        // DUP
6103        // DROP
// Comment line
6D50        // IO@

"""

@pytest.fixture
def hex_file(tmp_path):
    # Create a temporary hex file
    hex_file = tmp_path / "test.hex"
    hex_file.write_text(TEST_HEX_DATA)
    return hex_file

def test_hex_to_coe(hex_file, capsys):
    # Call the function
    hex_to_coe(hex_file)
    
    # Get the captured output
    captured = capsys.readouterr()
    
    # Expected output
    expected = """\
memory_initialization_radix=16;
memory_initialization_vector=
6000,
6011,
6103,
6D50;"""
    
    assert captured.out.strip() == expected

def test_hex_to_mif(hex_file, capsys):
    # Call the function
    hex_to_mif(hex_file)
    
    # Get the captured output
    captured = capsys.readouterr()
    
    # Expected output - each line should be 16-bit binary
    expected = """\
0110000000000000
0110000000010001
0110000100000011
0110110101010000"""
    
    assert captured.out.strip() == expected

def test_hex_file_not_found():
    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        hex_to_coe("nonexistent.hex")

def test_invalid_hex_value(tmp_path):
    # Create a hex file with invalid hex value
    bad_hex = tmp_path / "bad.hex"
    bad_hex.write_text("ZZZZ")
    
    # Should raise ValueError
    with pytest.raises(ValueError):
        hex_to_coe(bad_hex)