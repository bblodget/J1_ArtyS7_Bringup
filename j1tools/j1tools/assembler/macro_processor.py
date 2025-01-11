"""
Macro processing for J1 assembler.
Handles macro definitions, expansion, and validation.
"""

import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from lark import Token, Tree
from dataclasses import dataclass
from .asm_types import InstructionType, InstructionMetadata


@dataclass
class MacroDefinition:
    """Represents a macro definition with its attributes."""

    stack_effect: Optional[str]  # Optional stack effect comment
    body: List[InstructionMetadata]  # List of instructions that make up the macro
    defined_at: str  # Location where macro was defined (file:line)


class MacroProcessor:
    def __init__(self, debug: bool = False):
        # Dictionary to store macro definitions
        # Key: macro name
        # Value: MacroDefinition object
        self.macros: Dict[str, MacroDefinition] = {}

        # Set to track macros being expanded (prevents infinite recursion)
        self.expanding: Set[str] = set()

        # Current file being processed (for error messages)
        self.current_file = "<unknown>"

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

    def process_macro_def(self, items: List[Any]) -> None:
        """
        Process a macro definition from the parser.

        Args:
            items: List of items from the parser representing a macro definition
        """
        self.logger.debug(f"Processing macro definition: {items}")

        # Extract macro name (items[1] is the IDENT token)
        name_token = items[1]
        name = str(name_token)

        # Extract stack effect comment if present
        stack_effect = None
        body_start = 2
        if (
            len(items) > 3
            and isinstance(items[2], Token)
            and items[2].type == "STACK_COMMENT"
        ):
            stack_effect = str(items[2])
            body_start = 3

        # Collect macro body instructions (everything before the semicolon)
        raw_body = items[body_start:-1]  # -1 to skip the semicolon

        # Extract the actual instructions from the Tree structure
        body = []
        tree_body = raw_body[0]
        if isinstance(tree_body, Tree):
            for child in tree_body.children:
                if isinstance(child, InstructionMetadata):
                    body.append(child)
                else:
                    raise ValueError(
                        f"{self.current_file}:{name_token.line}:{name_token.column}: "
                        f"Expected InstructionMetadata in macro body, got {type(child)}"
                    )
        else:
            raise ValueError(
                f"{self.current_file}:{name_token.line}:{name_token.column}: "
                f"Unexpected macro body structure: {tree_body}"
            )

        # Define the macro
        self.define_macro(name, body, stack_effect, name_token)

    def expand_macro(self, name: str, token: Token) -> List[InstructionMetadata]:
        """Expand a macro into its constituent instructions."""
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
