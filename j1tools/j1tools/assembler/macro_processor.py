"""
Macro processing for J1 assembler.
Handles macro definitions, expansion, and validation.
"""

import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from lark import Token, Tree
from dataclasses import dataclass
from .asm_types import InstructionType, InstructionMetadata
from .address_space import AddressSpace

@dataclass
class MacroDefinition:
    """Represents a macro definition with its attributes."""

    stack_effect: Optional[str]  # Optional stack effect comment
    body: List[InstructionMetadata]  # List of instructions that make up the macro
    defined_at: str  # Location where macro was defined (file:line)


class MacroProcessor:
    def __init__(self, addr_space: AddressSpace, debug: bool = False) -> None:
        # Dictionary to store macro definitions
        # Key: macro name
        # Value: MacroDefinition object
        self.macros: Dict[str, MacroDefinition] = {}

        # Set to track macros being expanded (prevents infinite recursion)
        self.expanding: Set[str] = set()

        # Current file being processed (for error messages)
        self.current_file: str = "<unknown>"

        # Address space
        self.addr_space = addr_space

        # Setup logging
        self.logger = logging.getLogger("j1asm.macro")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def set_current_file(self, filename: str) -> None:
        """Set the current file being processed for error reporting."""
        self.current_file = filename

    def define_macro(
        self,
        name: str,
        body: List[InstructionMetadata],
        stack_effect: Optional[str] = None,
        token: Optional[Token] = None,
    ) -> None:
        """
        Define a new macro.

        Args:
            name: Name of the macro
            body: List of instructions that make up the macro
            stack_effect: Optional stack effect comment
            token: Token for error reporting
        """
        if name in self.macros:
            location = token.line if token else "unknown"
            raise ValueError(
                f"{self.current_file}:{location}: "
                f"Duplicate macro definition: {name}"
            )

        self.logger.debug(f"Defining macro {name} with body: {body}")
        self.macros[name] = MacroDefinition(
            stack_effect=stack_effect,
            body=body,
            defined_at=f"{self.current_file}:{token.line if token else 'unknown'}",
        )

    def process_macro_def(self, items):
        """Process a macro definition."""
        self.logger.debug(f"Processing macro items: {items}")
        
        # Handle different item counts based on whether stack_comment is present
        if len(items) == 4:
            # No stack comment present
            macro_token, name_token, body_tree, end_token = items
            stack_comment = None
        elif len(items) == 5:
            # Stack comment present
            macro_token, name_token, stack_comment, body_tree, end_token = items
        else:
            raise ValueError(f"Invalid macro definition structure: {items}")

        # Extract instructions from macro body
        if not isinstance(body_tree, Tree) or body_tree.data != "macro_body":
            raise ValueError(f"Invalid macro body structure")

        # Get the instruction list from the body
        instructions = body_tree.children

        # Flatten and validate instructions
        flattened_instructions = []
        for instr in instructions:
            if isinstance(instr, list):
                # TODO: Why does this happen?
                if len(instr) == 1:
                    self.addr_space.undo_advance()
                    instr[0].word_addr = -1;
                    flattened_instructions.append(instr[0])
                else:
                    raise ValueError(
                        f"{self.current_file}:{name_token.line}:{name_token.column}: "
                        f"GOT HERE: Expected InstructionMetadata or list in macro body, got {type(instr)}"
                    )
            elif isinstance(instr, InstructionMetadata):
                # We are just defining a macro, so undo the advance of the address space
                self.addr_space.undo_advance()

                # Ther is no address for this instruction yet
                instr.word_addr = -1;

                flattened_instructions.append(instr)
            else:
                raise ValueError(
                    f"{self.current_file}:{name_token.line}:{name_token.column}: "
                    f"Expected InstructionMetadata or list in macro body, got {type(instr)}"
                )

        # Store the macro definition
        self.define_macro(
            str(name_token),
            flattened_instructions,
            str(stack_comment) if stack_comment else None,
            name_token,
        )

    def expand_macro(self, name: str, token: Token) -> List[InstructionMetadata]:
        """
        Expand a macro into its constituent instructions.

        Args:
            name: Name of the macro to expand
            token: Token for error reporting and location information

        Returns:
            List of expanded instructions

        Raises:
            ValueError: If macro is unknown or recursive expansion is detected
        """
        if name not in self.macros:
            raise ValueError(f"Unknown macro: {name}")

        if name in self.expanding:
            raise ValueError(f"Recursive macro expansion detected: {name}")

        self.expanding.add(name)
        macro = self.macros[name]

        # Create new instructions based on the macro's body
        expanded = []
        for instr in macro.body:
            # Create a new instruction with updated metadata
            new_instr = InstructionMetadata(
                type=instr.type,
                value=instr.value,
                token=token,
                filename=instr.filename,
                line=token.line,
                column=token.column,
                source_line=instr.source_line,
                instr_text=instr.instr_text,
                macro_name=name,
                opt_name=None,
                label_name=None,
                word_addr=self.addr_space.advance()
            )
            expanded.append(new_instr)

        self.expanding.remove(name)
        return expanded

    def is_macro(self, name: str) -> bool:
        """Check if a name refers to a defined macro."""
        return name in self.macros

    def get_macro_info(self, name: str) -> Optional[MacroDefinition]:
        """Get information about a macro if it exists."""
        return self.macros.get(name)
