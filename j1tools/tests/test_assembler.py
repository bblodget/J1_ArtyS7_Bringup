import pytest
from j1tools.assembler.asm import J1Assembler

# Test assembly code
TEST_ASM = """
start:          ; Program start
    NOP         ; Do nothing
    DUP         ; Duplicate top of stack
    DROP        ; Drop top of stack
    LIT #1234   ; Push value
    IO@         ; Read from IO
    IO!         ; Write to IO
loop:
    JMP loop    ; Infinite loop
    RET         ; Never reached
"""

@pytest.fixture
def asm_file(tmp_path):
    # Create a temporary assembly file
    asm_file = tmp_path / "test.asm"
    asm_file.write_text(TEST_ASM)
    return asm_file

def test_basic_instructions(asm_file):
    asm = J1Assembler()
    code, comments = asm.assemble(asm_file)
    
    # Expected opcodes
    expected = [
        0x6000,  # NOP
        0x6011,  # DUP
        0x6103,  # DROP
        0xD234,  # LIT #1234
        0x6D50,  # IO@
        0x6040,  # IO!
        0x0006,  # JMP loop (address 6)
        0x6080,  # RET
    ]
    
    assert code == expected
    assert comments[0] == "Do nothing"
    assert comments[3] == "Push 1234"

def test_labels(asm_file):
    asm = J1Assembler()
    code, _ = asm.assemble(asm_file)
    
    # Check that JMP loop points to correct address
    assert code[6] & 0x1FFF == 6  # Lower 13 bits should be loop address

def test_file_not_found():
    asm = J1Assembler()
    with pytest.raises(FileNotFoundError):
        asm.assemble("nonexistent.asm")

def test_invalid_instruction(tmp_path):
    # Create assembly file with invalid instruction
    bad_asm = tmp_path / "bad.asm"
    bad_asm.write_text("INVALID_OP")
    
    asm = J1Assembler()
    with pytest.raises(KeyError):
        asm.assemble(bad_asm)

def test_invalid_literal(tmp_path):
    # Create assembly file with invalid literal
    bad_asm = tmp_path / "bad.asm"
    bad_asm.write_text("LIT #ZZZZ")
    
    asm = J1Assembler()
    with pytest.raises(ValueError):
        asm.assemble(bad_asm)

def test_missing_label(tmp_path):
    # Create assembly file with undefined label
    bad_asm = tmp_path / "bad.asm"
    bad_asm.write_text("JMP missing_label")
    
    asm = J1Assembler()
    code, _ = asm.assemble(bad_asm)
    
    # Should default to address 0
    assert code[0] & 0x1FFF == 0