"""
J1 CPU Instruction Set Definition
Based on instructionset-16kb-dualport.fs
"""

# ALU Operations (base operations without stack effects)
ALU_OPS = {
    "T": 0x0000,
    "N": 0x0100,
    "T+N": 0x0200,
    "T&N": 0x0300,
    "T|N": 0x0400,
    "T^N": 0x0500,
    "~T": 0x0600,
    "N==T": 0x0700,
    "N<T": 0x0800,
    #"T2/": 0x0900,
    #"T2*": 0x0A00,
    ">>": 0x0900,
    "<<": 0x0A00,
    "rT": 0x0B00,
    "N-T": 0x0C00,
    "io[T]": 0x0D00,
    "status": 0x0E00,
    "Nu<T": 0x0F00,
    # Specials for HX8K
    "NlshiftT": 0x1000,
    "NrshiftT": 0x1100,
    "NarshiftT": 0x1200,
    "rstatus": 0x1300,
    "L-UM*": 0x1400,
    "H-UM*": 0x1500,
    "T+1": 0x1600,
    "T-1": 0x1700,
    "3OS": 0x1800,
    "mem[T]": 0x1900,
}

# Stack Effects and Return Modifiers
STACK_EFFECTS = {
    "T->N": 0x0010,
    "T->R": 0x0020,
    "N->[T]": 0x0030,
    "N->io[T]": 0x0040,
    "IORD": 0x0050,
    "fDINT": 0x0060,
    "fEINT": 0x0070,
    "RET": 0x0080,
}

# Data Stack Delta
D_EFFECTS = {
    "d+0": 0x0000,  # unchanged
    "d+1": 0x0001,  # push
    "d-2": 0x0002,
    "d-1": 0x0003,  # pop
}

# Return Stack Delta
R_EFFECTS = {
    "r+0": 0x0000,  # unchanged
    "r+1": 0x0004,  # push
    "r-2": 0x0008,
    "r-1": 0x000C,  # pop
}

# Instruction Type Bases
INST_TYPES = {
    "imm": 0x8000,  # Immediate value
    "alu": 0x6000,  # ALU operation
    "ubranch": 0x0000,  # Unconditional branch
    "0branch": 0x2000,  # Conditional branch
    "scall": 0x4000,  # Subroutine call
}

# High-Level Words (with stack effects included)
HIGH_LEVEL_WORDS = {
    # Stack manipulation
    "DUP": INST_TYPES["alu"] | ALU_OPS["T"] | STACK_EFFECTS["T->N"] | D_EFFECTS["d+1"],
    "DROP": INST_TYPES["alu"] | ALU_OPS["N"] | D_EFFECTS["d-1"],
    "SWAP": INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->N"],
    "OVER": INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->N"] | D_EFFECTS["d+1"],
    "NIP": INST_TYPES["alu"] | ALU_OPS["T"] | D_EFFECTS["d-1"],
    # Arithmetic/Logic
    "ADD": INST_TYPES["alu"] | ALU_OPS["T+N"] | D_EFFECTS["d-1"],
    "SUBTRACT": INST_TYPES["alu"] | ALU_OPS["N-T"] | D_EFFECTS["d-1"],
    "AND": INST_TYPES["alu"] | ALU_OPS["T&N"] | D_EFFECTS["d-1"],
    "OR": INST_TYPES["alu"] | ALU_OPS["T|N"] | D_EFFECTS["d-1"],
    "XOR": INST_TYPES["alu"] | ALU_OPS["T^N"] | D_EFFECTS["d-1"],
    "INVERT": INST_TYPES["alu"] | ALU_OPS["~T"],
    "1+": INST_TYPES["alu"] | ALU_OPS["T+1"],
    "1-": INST_TYPES["alu"] | ALU_OPS["T-1"],
    "2*": INST_TYPES["alu"] | ALU_OPS["<<"],
    "2/": INST_TYPES["alu"] | ALU_OPS[">>"],
}