"""
Type definitions for J1 assembler.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List
from lark import Token


class InstructionType(Enum):
    """Types of instructions in the J1 assembly."""

    BYTE_CODE = auto()
    LABEL = auto()
    JUMP = auto()
    MACRO_DEF = auto()
    MACRO_CALL = auto()
    ALU = auto()
    SUBROUTINE_DEF = auto()  


@dataclass
class Modifier:
    """Represents a J1 instruction modifier."""

    value: int  # The machine code value
    text: str  # The original text representation
    token: Token  # The original token for error reporting


@dataclass
class ModifierList:
    """Represents a list of modifiers combined into a single value."""

    value: int  # Combined machine code value
    text: str  # Combined text representation (comma-separated)
    tokens: List[Token]  # Original tokens for error reporting


@dataclass
class InstructionMetadata:
    """Represents metadata about an instruction including its value and source information."""

    type: InstructionType  # Type of instruction
    value: int  # The bytecode/value
    token: Token  # The original token
    filename: str  # Source file
    line: int  # Line number
    column: int  # Column number
    source_line: str  # Complete source line
    instr_text: str  # Clean instruction text for listing

    # Optional metadata
    macro_name: Optional[str] = None  # Name of macro if from macro expansion
    opt_name: Optional[str] = None  # Name of optimization if applied
    label_name: Optional[str] = None  # Name of label (for LABEL type)

    @classmethod
    def from_token(
        cls,
        inst_type: InstructionType,
        value: int,
        token: Token,
        filename: str,
        source_lines: List[str],
        instr_text: str,
        **kwargs
    ) -> "InstructionMetadata":
        """Factory method to create metadata from a token."""
        return cls(
            type=inst_type,
            value=value,
            token=token,
            filename=filename,
            line=token.line,
            column=token.column,
            source_line=source_lines[token.line - 1],
            instr_text=instr_text,
            **kwargs
        )


@dataclass
class IncludeStack:
    """Tracks include file processing state."""

    filename: str
    line_number: int
    source_lines: List[str]


@dataclass
class AssemblerState:
    """Global state for the assembler."""

    current_file: str
    include_paths: List[str]
    include_stack: List[IncludeStack]
    source_lines: List[str]
