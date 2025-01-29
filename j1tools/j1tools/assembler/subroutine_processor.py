"""
Subroutine processing for J1 assembler.
Handles subroutine definitions, calls, and validation.
"""

import logging
from typing import Dict, List, Set, Optional
from lark import Token, Tree
from dataclasses import dataclass
from .asm_types import InstructionMetadata, InstructionType


@dataclass
class SubroutineDefinition:
    """Represents a subroutine definition with its attributes."""

    stack_effect: Optional[str]  # Optional stack effect comment
    body: List[InstructionMetadata]  # List of instructions in the subroutine
    defined_at: str  # Location where subroutine was defined (file:line)
    entry_point: int  # Address where subroutine starts


class SubroutineProcessor:
    def __init__(self, debug: bool = False) -> None:
        self.subroutines: Dict[str, SubroutineDefinition] = {}
        self.current_file: str = "<unknown>"

        # Setup logging
        self.logger = logging.getLogger("j1asm.subroutine")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def set_current_file(self, filename: str) -> None:
        """Set the current file being processed for error reporting."""
        self.current_file = filename

    def define_subroutine(
        self,
        name: str,
        body: List[InstructionMetadata],
        entry_point: int,
        stack_effect: Optional[str] = None,
        token: Optional[Token] = None,
    ) -> None:
        """Define a new subroutine."""
        if name in self.subroutines:
            location = token.line if token else "unknown"
            raise ValueError(
                f"{self.current_file}:{location}: "
                f"Duplicate subroutine definition: {name}"
            )

        self.subroutines[name] = SubroutineDefinition(
            stack_effect=stack_effect,
            body=body,
            entry_point=entry_point,
            defined_at=f"{self.current_file}:{token.line if token else 'unknown'}",
        )

    def expand_subroutine_call(self, name: str, token: Token) -> InstructionMetadata:
        """Convert a subroutine call into a CALL instruction."""
        if name not in self.subroutines:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Unknown subroutine: {name}"
            )

        # Create a CALL instruction to the subroutine
        return InstructionMetadata.from_token(
            inst_type=InstructionType.JUMP,
            value=0x4000,  # CALL opcode
            token=token,
            filename=self.current_file,
            source_lines=[],  # Will be filled in by assembler
            label_name=name,
            instr_text=f"CALL {name}",
        )

    def is_subroutine(self, name: str) -> bool:
        """Check if a name refers to a defined subroutine."""
        return name in self.subroutines

    def get_subroutine_info(self, name: str) -> Optional[SubroutineDefinition]:
        """Get information about a subroutine if it exists."""
        return self.subroutines.get(name)

    def process_subroutine_def(self, items) -> List[InstructionMetadata]:
        """Process a subroutine definition and return its instructions."""
        colon_token = items[0]  # COLON token
        name_token = items[1]  # IDENT token
        subroutine_name = str(name_token)

        # Get stack effect comment if present
        stack_effect = None
        for item in items:
            if isinstance(item, Token) and item.type == "STACK_COMMENT":
                stack_effect = str(item)
                break

        # Create a label for the subroutine
        label_metadata = InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,
            token=name_token,
            filename=self.current_file,
            source_lines=[],  # Will be filled by assembler
            instr_text=f"{subroutine_name}:",
            label_name=subroutine_name,
        )

        # Process the body instructions
        body_instructions = []
        for item in items:
            if isinstance(item, Tree):  # This is the instruction list
                self.logger.debug(f"\nProcessing subroutine body: ")
                children = item.children
                # Flatten nested lists of instructions
                for child in children:
                    if isinstance(child, list):
                        body_instructions.extend(child)
                    else:
                        body_instructions.append(child)

        # Add RET instruction at the end if not already present
        if not body_instructions or not self._is_return_instruction(
            body_instructions[-1]
        ):
            ret_token = name_token  # Reuse the name token for location info
            ret_inst = InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=0x0080,  # RET instruction value
                token=ret_token,
                filename=self.current_file,
                source_lines=[],  # Will be filled by assembler
                instr_text="RET",
            )
            body_instructions.append(ret_inst)

        # Store the subroutine definition (entry_point will be set by assembler)
        self.define_subroutine(
            name=subroutine_name,
            body=body_instructions,
            entry_point=-1,  # Will be updated by assembler
            stack_effect=stack_effect,
            token=name_token,
        )

        # Return the label and all body instructions
        return [label_metadata] + body_instructions

    def _is_return_instruction(self, inst: InstructionMetadata) -> bool:
        """Check if an instruction is a return instruction."""
        return (
            isinstance(inst, InstructionMetadata)
            and inst.type == InstructionType.BYTE_CODE
            and (inst.value & 0x0080) == 0x0080
        )  # Check for RET bit
