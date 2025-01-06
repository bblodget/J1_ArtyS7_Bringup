#!/usr/bin/env python

import sys
import logging
import argparse
import lark
from lark import Lark, Transformer, Tree, Token
from pathlib import Path
from .instructionset_16kb_dualport import (
    ALU_OPS,
    STACK_EFFECTS,
    D_EFFECTS,
    R_EFFECTS,
    INST_TYPES,
    JUMP_OPS,
)
import click


class J1Assembler(Transformer):
    def __init__(self, debug=False):
        super().__init__()
        self.labels = {}
        self.current_address = 0
        self.debug = debug
        self.current_file = "<unknown>"

        # Setup logging
        self.logger = logging.getLogger("j1asm")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        # Load the grammar
        grammar_path = Path(__file__).parent / "j1.lark"
        if not grammar_path.exists():
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}")

        try:
            self.parser = Lark.open(grammar_path, start="start")
            self.logger.debug(f"Loaded grammar from {grammar_path}")
        except Exception as e:
            raise Exception(f"Failed to load grammar: {e}")

    def parse(self, source, filename="<unknown>"):
        """Parse source code with optional filename for error reporting."""
        self.current_file = filename
        tree = self.parser.parse(source)
        self.logger.debug("\n=== Tokens ===")

        if self.debug:
            # Output all tokens in the tree
            for token in tree.scan_values(lambda v: isinstance(v, Token)):
                self.logger.debug(f"Token: {token.type} = '{token.value}'")

        return tree

    def program(self, statements):
        """Process all statements and resolve labels."""
        self.logger.debug(f"\nProgram statements: {statements}")

        # First pass: collect labels and instructions
        self.current_address = 0
        instructions = []

        for stmt in statements:
            self.logger.debug(
                f"\nProcessing statement at address {self.current_address}: {stmt}"
            )

            if isinstance(stmt, list):
                # Handle label + instruction pair
                label, instruction = stmt
                if label[0] == "label":
                    if label[1] in self.labels:
                        raise ValueError(f"Duplicate label: {label[1]}")
                    self.logger.debug(
                        f"Adding label {label[1]} at address {self.current_address}"
                    )
                    self.labels[label[1]] = self.current_address
                instructions.append(instruction)
                self.current_address += 1
            elif isinstance(stmt, tuple):
                # Handle standalone instruction
                if stmt[0] != "label":  # Skip standalone labels
                    instructions.append(stmt)
                    self.current_address += 1
            else:
                raise ValueError(f"Unexpected statement type: {type(stmt)}")

        self.logger.debug(f"\nCollected labels: {self.labels}")
        self.logger.debug(f"Instructions: {instructions}")

        # Second pass: resolve labels
        resolved = []
        current_addr = 0
        for inst in instructions:
            self.logger.debug(f"Processing instruction at {current_addr}: {inst}")

            type_, value = inst
            if type_ == "jump":
                jump_type, label, token = value
                if label not in self.labels:
                    raise ValueError(
                        f"{self.current_file}:{token.line}:{token.column}: "
                        f"Undefined label: {label}"
                    )
                resolved.append(jump_type | self.labels[label])
            elif type_ == "byte_code":
                resolved.append(value)
            else:
                raise ValueError(f"Unexpected instruction type: {type_}")
            current_addr += 1

        return resolved

    def statement(self, items):
        """
        Handles the 'statement' rule by processing both labels and instructions.
        A statement can be:
        - Just an instruction (1 item)
        - Label + instruction (2 items)
        """
        self.logger.debug(f"\nStatement items: {items}")

        if len(items) == 1:
            # Just an instruction
            return items[0]
        elif len(items) == 2:
            # Label + instruction pair
            label, instruction = items
            if label[0] != "label":
                raise ValueError(f"Expected label, got {label[0]}")
            self.logger.debug(f"Pairing label {label[1]} with instruction")
            # Return both as a list so program() can process them together
            return [label, instruction]
        else:
            raise ValueError(f"Unexpected statement format: {items}")

    def jump_op(self, items):
        """Handle jump operations with their labels."""
        op = str(items[0])
        label_type, label = items[1]  # Should be ("label", label_name)
        if op not in JUMP_OPS:
            raise ValueError(
                f"{self.current_file}:{items[0].line}:{items[0].column}: "
                f"Unknown jump operation: {op}"
            )
        if label_type != "label":
            raise ValueError(
                f"{self.current_file}:{items[0].line}:{items[0].column}: "
                f"Expected label reference, got {label_type}"
            )
        return (
            "jump",
            (JUMP_OPS[op], label, items[0]),
        )  # Include token for error reporting

    def instruction(self, items):
        """Handles the 'instruction' rule."""
        item = items[0]

        self.logger.debug(f"Processing instruction item: {item}")

        # Handle single instructions
        item_type, value = item
        token = item[2] if len(item) > 2 else None

        self.logger.debug(f"Processing instruction: {item_type} {value}")

        if item_type == "label":
            return item  # Pass through labels unchanged
        elif item_type == "jump":
            return item  # Pass through jump instructions
        elif item_type == "byte_code":
            return item  # Already final form

        if token:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Invalid instruction type: {item_type}"
            )
        raise ValueError(f"Invalid instruction type: {item_type}")

    def modifier(self, items):
        """Convert modifiers into their machine code representation with type."""
        token = items[0]
        mod = str(token)
        self.logger.debug(f"\nModifier: processing '{mod}'")

        if mod in STACK_EFFECTS:
            result = ("modifier", STACK_EFFECTS[mod])
        elif mod in D_EFFECTS:
            result = ("modifier", D_EFFECTS[mod])
        elif mod in R_EFFECTS:
            result = ("modifier", R_EFFECTS[mod])
        else:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Unknown modifier: {mod}"
            )

        self.logger.debug(f"Modifier result: {result}")
        return result

    def modifier_list(self, items):
        """Combines all modifiers into a single integer using bitwise OR."""
        self.logger.debug(f"\nModifier list items: {items}")

        result = 0
        for item in items:
            self.logger.debug(f"Processing modifier item: {item}")

            if isinstance(item, Token) and item.type == "COMMA":
                self.logger.debug("Skipping comma token")
                continue
            elif isinstance(item, tuple) and item[0] == "modifier":
                self.logger.debug(f"Adding modifier value: {item[1]:04x}")
                result |= item[1]
            else:
                token = item if isinstance(item, Token) else items[0]
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Expected modifier, got {item}"
                )

        self.logger.debug(f"Final modifier list result: ('modifier', {result:04x})")
        return ("modifier", result)

    def modifiers(self, items):
        """Process the modifiers rule (handles brackets)."""
        self.logger.debug(f"\nModifiers: processing items: {items}")
        # items[0] is LBRACKET, items[1] is modifier_list, items[2] is RBRACKET
        result = items[1]
        self.logger.debug(f"Modifiers result: {result}")
        return result

    def labelref(self, items):
        """Convert labelref rule into a tuple with the label name."""
        self.logger.debug(f"\nLabelref items: {items}")
        return ("label", str(items[0]))

    def label(self, items):
        """Convert label rule into a tuple with the label name."""
        self.logger.debug(f"\nLabel items: {items}")
        return ("label", str(items[0]))

    def number(self, items):
        """Convert number tokens to their machine code representation."""
        token = items[0]
        if token.type == "HEX":
            value = int(str(token)[2:], 16)
            # For hex literals, allow full 15-bit range
            if value > 0x7FFF:
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Hex number {value} out of range (0 to $7FFF)"
                    f"Negative numbers must be constructed manually using: "
                    f"#ABS 1- INVERT"
                )
            # Set the high bit to make a literal
            return ("byte_code", value | 0x8000)
        elif token.type == "DECIMAL":
            value = int(str(token)[1:], 10)
            if value < 0:
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Negative numbers must be constructed manually using: "
                    f"#ABS 1- INVERT"
                )
            return ("byte_code", 0x8000 | value)
        else:
            raise ValueError(f"Unknown number format: {token}")

    def basic_alu(self, items):
        """Convert basic_alu rule into its token."""
        # items[0] is the Token for the ALU operation
        return items[0]

    def alu_op(self, items):
        """Convert ALU operations into their machine code representation."""
        self.logger.debug("\nALU Operation:")
        self.logger.debug(f"Items: {items}")

        # Extract operation and modifiers
        token = items[0]  # Now this will be a Token, not a Tree
        base_op = token.value  # Use token.value to get the string
        modifiers = 0

        # Process modifiers if present
        if len(items) > 1:
            for item in items[1:]:
                if isinstance(item, tuple) and item[0] == "modifier":
                    modifiers |= item[1]
                else:
                    raise ValueError(
                        f"{self.current_file}:{token.line}:{token.column}: "
                        f"Expected modifier, got {item}"
                    )

        # Get the base ALU operation code
        if base_op not in ALU_OPS:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Unknown ALU operation '{base_op}'"
            )
        result = ALU_OPS[base_op]

        # Add modifiers
        result |= modifiers

        return ("byte_code", INST_TYPES["alu"] | result)

    def data_stack_delta(self, items):
        """Convert data stack delta rule into its token."""
        return items[0]

    def return_stack_delta(self, items):
        """Convert return stack delta rule into its token."""
        return items[0]

    def stack_delta(self, items):
        """Convert stack delta rule into its token."""
        return items[0]

    def stack_effect(self, items):
        """Convert stack effect rule into its token."""
        return items[0]


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option(
    "-o", "--output", type=click.Path(), help="Output file (default: aout.hex)"
)
@click.option("-d", "--debug", is_flag=True, help="Enable debug output")
def main(input, output, debug):
    """J1 Forth CPU Assembler"""
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(levelname)s: %(message)s",
            stream=sys.stderr,
        )
        logger = logging.getLogger("j1asm")

        # Set default output file if not specified
        output = output or "aout.hex"

        # Read the input file
        with open(input, "r") as f:
            source = f.read()
            logger.debug(f"Source code:\n{source}")

        logger.debug("Parsing source...")

        assembler = J1Assembler(debug=debug)
        try:
            tree = assembler.parse(source, filename=input)
            instructions = assembler.transform(tree)

            # Write output to specified file
            with open(output, "w") as f:
                for inst in instructions:
                    print(f"{inst:04x}", file=f)
            logger.info(f"Successfully wrote output to {output}")

        except lark.exceptions.UnexpectedInput as e:
            # Format Lark's parsing errors to match our style
            error_msg = str(e)
            if ", at line" in error_msg:
                error_msg = error_msg.split(", at line")[0]

            # Find the actual line with the error
            real_line = 0
            source_lines = source.splitlines()
            for i, line in enumerate(source_lines[: e.line - 1], 1):
                stripped = line.strip()
                if stripped and not stripped.startswith(";"):
                    real_line = i

            error_line = source_lines[real_line - 1]
            context = f"\n    {error_line}\n    {' ' * (e.column-1)}^"

            logger.error(f"{input}:{real_line}:{e.column}: {error_msg}")
            if debug:
                logger.debug(context)
            raise click.Abort()

    except Exception as e:
        logger.error(str(e))
        if debug:
            import traceback

            logger.debug(traceback.format_exc())
        raise click.Abort()


if __name__ == "__main__":
    main()
