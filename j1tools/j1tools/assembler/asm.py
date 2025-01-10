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
from typing import List, Tuple, Dict, Optional
from .macro_processor import MacroProcessor, InstructionData
from dataclasses import dataclass


@dataclass
class InstructionSource:
    filename: str
    line: int
    column: int
    source_line: str
    macro_name: Optional[str] = None
    opt_name: Optional[str] = None


class J1Assembler(Transformer):
    def __init__(self, debug=False):
        super().__init__()
        self.labels = {}
        self.current_address = 0
        self.debug = debug
        self.current_file = "<unknown>"
        # Add source line tracking
        self.source_lines = []

        # Add source line tracking
        # Dict to store source information for each instruction
        # Key: bytecode word address
        # Value: InstructionSource object
        self.instruction_sources: Dict[int, InstructionSource] = {}
        self.label_sources: Dict[int, InstructionSource] = {}

        # Add instruction tracking
        # List to store the assembled instructions (bytecode words)
        self.instructions: List[int] = []
        self.is_assembled = False

        # Setup logging
        self.logger = logging.getLogger("j1asm")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        # Initialize macro processor
        self.macro_processor = MacroProcessor(debug=debug)

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
        self.macro_processor.set_current_file(filename)  # Add this line
        # Store source lines for listing generation, removing trailing whitespace
        self.source_lines = [line.rstrip() for line in source.splitlines()]
        tree = self.parser.parse(source)
        self.logger.debug("\n=== Tokens ===")

        if self.debug:
            # Output all tokens in the tree
            for token in tree.scan_values(lambda v: isinstance(v, Token)):
                self.logger.debug(f"Token: {token.type} = '{token.value}'")

        return tree

    def program(self, statements):
        """Process all statements and resolve labels."""
        self.current_address = 0
        instructions = []

        # First pass: collect labels and flatten instructions
        for stmt in statements:
            self.logger.debug(f"Statement: {stmt}")

            if isinstance(stmt, tuple):
                item_type, value = stmt

                if item_type == "label":
                    # Store label with current address
                    label_name, label_token = value

                    # Check if label is already defined
                    if label_name in self.labels:
                        raise ValueError(
                            f"{self.current_file}:{label_token.line}:{label_token.column}: "
                            f"Duplicate label: {label_name}"
                        )

                    # Record label information
                    self.labels[label_name] = len(instructions)
                    self.label_sources[len(instructions)] = InstructionSource(
                        filename=self.current_file,
                        line=label_token.line,
                        column=label_token.column,
                        source_line=self.source_lines[label_token.line - 1],
                    )
                    continue  # Skip to next statement

                elif item_type == "macro_def":
                    continue  # Skip macro definitions
                elif item_type == "jump":
                    instructions.append(stmt)
                    # No source info for jump instructions
                    # We sill add it in the second pass
                    continue
                elif item_type == "byte_code":
                    # Now value should always be InstructionData
                    if not isinstance(value, InstructionData):
                        raise ValueError(f"Expected InstructionData, got {type(value)}")

                    token = value.token
                    self.instruction_sources[len(instructions)] = InstructionSource(
                        filename=self.current_file,
                        line=token.line,
                        column=token.column,
                        source_line=self.source_lines[token.line - 1],
                        macro_name=value.macro_name,
                    )
                    instructions.append(stmt)

            elif isinstance(stmt, list):
                # Handle macro expansions - each item in the list is a complete instruction
                for macro_inst in stmt:
                    if isinstance(macro_inst, tuple):
                        inst_type, value = macro_inst
                        if inst_type == "byte_code" and isinstance(
                            value, InstructionData
                        ):
                            token = value.token
                            self.instruction_sources[len(instructions)] = (
                                InstructionSource(
                                    filename=self.current_file,
                                    line=token.line,
                                    column=token.column,
                                    source_line=self.source_lines[token.line - 1],
                                    macro_name=value.macro_name,
                                )
                            )
                            instructions.append(macro_inst)
                        else:
                            raise ValueError(
                                f"{self.current_file}:{token.line}:{token.column}: "
                                f"Invalid macro instruction format: {macro_inst}"
                            )
                    else:
                        raise ValueError(
                            f"{self.current_file}: Invalid macro instruction type: {type(macro_inst)}"
                        )
            else:
                raise ValueError(f"Unexpected statement type: {type(stmt)}")

        self.logger.debug(f"\nCollected labels: {self.labels}")
        self.logger.debug(f"Instructions: {instructions}")

        # Second pass: resolve jumplabels
        resolved = []
        for current_addr, inst in enumerate(instructions):
            self.logger.debug(f"Processing instruction at {current_addr}: {inst}")

            type_, value = inst
            if type_ == "jump":
                jump_type, label, token = value
                if label not in self.labels:
                    raise ValueError(
                        f"{self.current_file}:{token.line}:{token.column}: "
                        f"Undefined label: {label}"
                    )
                machine_code = jump_type | self.labels[label]
                # Create InstructionData for jumps too
                resolved.append(machine_code)
                self.instruction_sources[len(resolved) - 1] = InstructionSource(
                    filename=self.current_file,
                    line=token.line,
                    column=token.column,
                    source_line=self.source_lines[token.line - 1],
                )
            elif type_ == "byte_code":
                resolved.append(value.value)

        # Store resolved instructions and mark as assembled
        self.instructions = resolved
        self.is_assembled = True
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

        # Handle case where we get a list of instructions (from macro expansion)
        if isinstance(item, list):
            return item  # Pass through list of instructions unchanged

        # Handle single instructions
        item_type, value = item
        token = value[1] if isinstance(value, tuple) else None

        self.logger.debug(f"Processing instruction: {item_type} {value}")

        if item_type == "label":
            return item  # Pass through labels unchanged
        elif item_type == "jump":
            return item  # Pass through jump instructions
        elif item_type == "byte_code":
            return item  # Already final form
        elif item_type == "macro_call":
            macro_name = value[0]
            if not self.macro_processor.is_macro(macro_name):
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Unknown macro: {macro_name}"
                )
            return item  # Pass through macro calls

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
        token = items[0]  # This is the IDENT tocken
        return ("label", (str(token), token))

    def number(self, items):
        """Convert number tokens to their machine code representation."""
        token = items[0]
        if token.type == "HEX":
            value = int(str(token)[2:], 16)
            if value > 0x7FFF:
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Hex number {value} out of range (0 to $7FFF)"
                )
            machine_code = value | 0x8000
            return ("byte_code", InstructionData(value=machine_code, token=token))
        elif token.type == "DECIMAL":
            value = int(str(token)[1:], 10)
            if value < 0:
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Negative numbers must be constructed manually"
                )
                # TODO: Generate instructions for negative number
                # abs_value = abs(value)
                # return [
                #    ("byte_code", (0x8000 | abs_value, token)),  # Push absolute value
                #    ("byte_code", (24577, token)),               # T 1-
                #    ("byte_code", (24584, token)),               # INVERT
                # ]
            machine_code = 0x8000 | value
            return ("byte_code", InstructionData(value=machine_code, token=token))
        else:
            raise ValueError(f"Unknown number format: {token}")

    def basic_alu(self, items):
        """Convert basic_alu rule into its token."""
        # items[0] is the Token for the ALU operation
        return items[0]

    def alu_op(self, items):
        """Convert ALU operations into their machine code representation."""
        token = items[0]
        base_op = token.value
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
        result = ALU_OPS[base_op] | modifiers | INST_TYPES["alu"]
        return ("byte_code", InstructionData(value=result, token=token))

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

    def generate_listing_line(
        self,
        addr: int,
        code: int,
        source_info: InstructionSource,
        is_label: bool = False,
    ) -> str:
        """Generate a single line for the listing file with explicit field spacing."""
        addr_space = " " * 5
        mcode_space = " " * 10
        line_num_space = " " * 2

        line_info = f"{source_info.line:2d}:{source_info.column:<3d}"
        source_line = source_info.source_line

        # Add macro/optimization information to comments
        if source_info.macro_name:
            if "//" in source_line:
                pre_comment, comment = source_line.split("//", 1)
                source_line = f"{pre_comment}// (macro: {source_info.macro_name}) {comment.lstrip()}"
            else:
                source_line = f"{source_line} // (macro: {source_info.macro_name})"

        if is_label:
            line = f"{addr:04x}{addr_space}----{mcode_space}{line_info}{line_num_space}{source_line}\n"
        else:
            line = f"{addr:04x}{addr_space}{code:04x}{mcode_space}{line_info}{line_num_space}{source_line}\n"
        return line

    def generate_listing(self, output_file: str) -> None:
        """Generate listing file showing address, machine code, and source."""
        if not self.is_assembled:
            raise ValueError("Cannot generate listing before assembling")

        with open(output_file, "w") as f:
            # Write header
            f.write("Address  Machine Code  #:col  Source\n")
            f.write("-" * 50 + "\n")

            # Write each instruction with its source
            for addr, code in enumerate(self.instructions):
                if addr in self.instruction_sources:
                    source_info = self.instruction_sources[addr]
                    line = self.generate_listing_line(addr, code, source_info)
                    f.write(line)

    def generate_symbols(self, output_file: str):
        """Generate symbol file showing addresses and their associated labels."""
        if not self.is_assembled:
            raise ValueError("Cannot generate symbols before assembling")

        with open(output_file, "w") as f:
            # Sort symbols by address for readability
            sorted_symbols = sorted(self.labels.items(), key=lambda x: x[1])
            for symbol, addr in sorted_symbols:
                print(f"{addr:04x} {symbol}", file=f)

    def generate_output(self, output_file: str):
        """Generate output file containing machine code in hex format."""
        if not self.is_assembled:
            raise ValueError("Cannot generate output before assembling")

        with open(output_file, "w") as f:
            for inst in self.instructions:
                print(f"{inst:04x}", file=f)

    def macro_def(self, items):
        """Handle macro definitions by delegating to macro processor."""
        self.logger.debug(f"Processing macro definition: {items}")
        macro_token = items[0]  # MACRO token
        name_token = items[1]  # IDENT token
        macro_name = str(name_token)

        # Process the macro definition
        self.macro_processor.process_macro_def(items)

        # Return a tuple that matches our other instruction patterns
        return ("macro_def", (macro_name, name_token))

    def macro_call(self, items):
        """Handle macro invocations."""
        token = items[0]
        macro_name = str(token)

        # Get expanded instructions directly
        return self.macro_processor.expand_macro(macro_name, token)


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option(
    "-o", "--output", type=click.Path(), help="Output file (default: aout.hex)"
)
@click.option("-d", "--debug", is_flag=True, help="Enable debug output")
@click.option("--symbols", is_flag=True, help="Generate symbol file (.sym)")
@click.option("--listing", is_flag=True, help="Generate listing file (.lst)")
def main(input, output, debug, symbols, listing):
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
            assembler.generate_output(output)
            logger.info(f"Successfully wrote output to {output}")

            # Generate symbol file if requested
            if symbols:
                sym_file = Path(output).with_suffix(".sym")
                assembler.generate_symbols(sym_file)
                logger.info(f"Generated symbol file: {sym_file}")

            # Generate listing file if requested
            if listing:
                lst_file = Path(output).with_suffix(".lst")
                assembler.generate_listing(lst_file)
                logger.info(f"Generated listing file: {lst_file}")

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
