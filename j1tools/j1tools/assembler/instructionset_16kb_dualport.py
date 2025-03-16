"""
J1 CPU Instruction Set Definition
Based on instructionset-16kb-dualport.fs
"""

# ALU Operations (base operations without stack effects)
ALU_OPS = {
    "T": 0x0000,      # Return top of stack (TOS)
    "N": 0x0100,      # Return next on stack (NOS)
    "T+N": 0x0200,    # Add TOS and NOS
    "T&N": 0x0300,    # Bitwise AND of TOS and NOS
    "T|N": 0x0400,    # Bitwise OR of TOS and NOS
    "T^N": 0x0500,    # Bitwise XOR of TOS and NOS
    "~T": 0x0600,     # Bitwise invert of TOS
    "N==T": 0x0700,   # Equality comparison: 0xFFFF if NOS equals TOS, else 0x0000
    "N<T": 0x0800,    # Signed less than: 0xFFFF if NOS < TOS, else 0x0000
    "T2/": 0x0900,    # Arithmetic right shift TOS by 1 bit (divide by 2 with sign extension)
    "T2*": 0x0A00,    # Left shift TOS by 1 bit (multiply by 2)
    "rT": 0x0B00,     # Return top of return stack
    "N-T": 0x0C00,    # Subtract TOS from NOS
    "io[T]": 0x0D00,  # Read from I/O port addressed by TOS
    "status": 0x0E00, # Return data stack depth
    "Nu<T": 0x0F00,   # Unsigned less than: 0xFFFF if NOS < TOS (unsigned), else 0x0000
    
    # Specials for HX8K
    "NlshiftT": 0x1000,  # Left shift NOS by TOS bits
    "NrshiftT": 0x1100,  # Right shift NOS by TOS bits (logical)
    "NarshiftT": 0x1200, # Arithmetic right shift NOS by TOS bits (with sign extension)
    "rstatus": 0x1300,   # Return return-stack depth
    "L-UM*": 0x1400,     # Low 16 bits of unsigned 16x16->32 multiplication of TOS and NOS
    "H-UM*": 0x1500,     # High 16 bits of unsigned 16x16->32 multiplication of TOS and NOS
    "T+1": 0x1600,       # Increment TOS by 1
    "T-1": 0x1700,       # Decrement TOS by 1
    "3OS": 0x1800,       # Return third item on stack
    "mem[T]": 0x1900,    # Read from memory location addressed by TOS (fetch)
}

# Stack Effects and Return Modifiers
STACK_EFFECTS = {
    "T->N": 0x0010,    # Copy TOS to NOS
    "T->R": 0x0020,    # Push TOS to return stack
    "N->[T]": 0x0030,  # Store NOS to memory at address TOS
    "N->io[T]": 0x0040, # Write NOS to I/O port at address TOS
    "IORD": 0x0050,    # Flag to indicate I/O read operation
    "fDINT": 0x0060,   # Disable interrupts
    "fEINT": 0x0070,   # Enable interrupts
    "RET": 0x0080,     # Return from subroutine
}

# Data Stack Delta
D_EFFECTS = {
    "d+0": 0x0000,  # Data stack unchanged
    "d+1": 0x0001,  # Push to data stack (increment stack size)
    "d-2": 0x0002,  # Pop two items from data stack (decrement stack size by 2)
    "d-1": 0x0003,  # Pop from data stack (decrement stack size)
}

# Return Stack Delta
R_EFFECTS = {
    "r+0": 0x0000,  # Return stack unchanged
    "r+1": 0x0004,  # Push to return stack (increment return stack size)
    "r-2": 0x0008,  # Pop two items from return stack (decrement return stack size by 2)
    "r-1": 0x000C,  # Pop from return stack (decrement return stack size)
}

# Instruction Type Bases
INST_TYPES = {
    "imm": 0x8000,    # Immediate value (literal)
    "alu": 0x6000,    # ALU operation
    "ubranch": 0x0000, # Unconditional branch (JMP)
    "0branch": 0x2000, # Conditional branch (ZJMP) - jump if TOS is zero
    "scall": 0x4000,   # Subroutine call (CALL)
}

# Jump operation mapping to instruction types
JUMP_OPS = {
    "JMP": INST_TYPES["ubranch"],  # 0x0000
    "ZJMP": INST_TYPES["0branch"],  # 0x2000
    "CALL": INST_TYPES["scall"],  # 0x4000
}
