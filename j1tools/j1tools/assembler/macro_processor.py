"""
Macro processing for J1 assembler.
Handles macro definitions, expansion, and validation.
"""

import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from lark import Token, Tree


class MacroProcessor:
    def __init__(self, debug: bool = False):
        # Dictionary to store macro definitions
        # Key: macro name
        # Value: Dict containing 'stack_effect', 'body', and 'defined_at'
        self.macros: Dict[str, Dict[str, Any]] = {}

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
        body: List[Any],
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
        self.macros[name] = {
            "stack_effect": stack_effect,
            "body": body,
            "defined_at": f"{self.current_file}:{token.line if token else 'unknown'}",
        }

    def process_macro_def(self, items: List[Any]) -> None:
        """
        Process a macro definition from the parser.

        Args:
            items: List of items from the parser representing a macro definition
        """
        self.logger.debug(f"Processing macro definition: {items}")

        # Extract macro name (items[1] is the IDENT token)
        name = str(items[1])

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
        body = items[body_start:-1]  # -1 to skip the semicolon

        # Define the macro
        self.define_macro(name, body, stack_effect, items[1])

    def expand_macro(self, name: str, token: Token) -> List[Any]:
        """
        Expand a macro invocation into its constituent instructions.

        Args:
            name: Name of the macro to expand
            token: Token for error reporting

        Returns:
            List of expanded instructions
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

            # Return the expanded instructions
            expanded = []
            for inst in macro["body"]:
                if isinstance(inst, Tree):
                    # Process each instruction in the macro_body Tree
                    for child in inst.children:
                        if isinstance(child, tuple):
                            if child[0] == "label":
                                raise ValueError(
                                    f"{self.current_file}:{token.line}:{token.column}: "
                                    f"Labels are not allowed inside macros: {name}"
                                )
                            elif child[0] == "macro_def":
                                raise ValueError(
                                    f"{self.current_file}:{token.line}:{token.column}: "
                                    f"Macros are not allowed inside macros: {name}"
                                )
                            elif child[0] == "macro_call":
                                raise ValueError(
                                    f"{self.current_file}:{token.line}:{token.column}: "
                                    f"Macros are not allowed inside macros: {name}"
                                )
                            else:
                                expanded.append(child)
                        else:
                            raise ValueError(
                                f"{self.current_file}:{token.line}:{token.column}: "
                                f"Invalid instruction inside macro: {child}"
                            )
                else:
                    raise ValueError(
                        f"{self.current_file}:{token.line}:{token.column}: "
                        f"Invalid macro body structure: {inst}"
                    )

            self.logger.debug(f"Expanded {name} to: {expanded}")
            return expanded

        finally:
            self.expanding.remove(name)

    def is_macro(self, name: str) -> bool:
        """Check if a name refers to a defined macro."""
        return name in self.macros

    def get_macro_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a macro if it exists."""
        return self.macros.get(name)
