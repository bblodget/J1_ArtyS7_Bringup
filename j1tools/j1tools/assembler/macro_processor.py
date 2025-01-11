"""
Macro processing for J1 assembler.
Handles macro definitions, expansion, and validation.
"""

import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from lark import Token, Tree
from dataclasses import dataclass
from .instruction_metadata import InstructionMetadata, InstructionType


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
        """
        Expand a macro invocation into its constituent instructions.

        Args:
            name: Name of the macro to expand
            token: Token for error reporting

        Returns:
            List of expanded instructions as InstructionMetadata objects
        """
        if name not in self.macros:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Undefined macro: {name}"
            )

        if name in self.expanding:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Recursive macro expansion detected: {name}"
            )

        self.expanding.add(name)
        try:
            macro = self.macros[name]
            self.logger.debug(f"Expanding macro {name}: {macro}")

            # Validate each instruction in the body
            expanded = []
            for inst in macro.body:
                if isinstance(inst, InstructionMetadata):
                    # Create new metadata with macro name
                    new_metadata = InstructionMetadata(
                        type=inst.type,
                        value=inst.value,
                        token=inst.token,
                        filename=inst.filename,
                        line=inst.line,
                        column=inst.column,
                        source_line=inst.source_line,
                        macro_name=name,
                    )
                    expanded.append(new_metadata)
                else:
                    raise ValueError(f"Expected InstructionMetadata, got {type(inst)}")

            self.logger.debug(f"Expanded {name} to: {expanded}")
            return expanded

        finally:
            self.expanding.remove(name)

    def is_macro(self, name: str) -> bool:
        """Check if a name refers to a defined macro."""
        return name in self.macros

    def get_macro_info(self, name: str) -> Optional[MacroDefinition]:
        """Get information about a macro if it exists."""
        return self.macros.get(name)
