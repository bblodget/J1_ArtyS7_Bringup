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
from typing import List, Tuple, Dict, Optional, Union
from .asm_types import (
    InstructionType,
    InstructionMetadata,
    Modifier,
    ModifierList,
    IncludeStack,
)
from .macro_processor import MacroProcessor
from .config import AssemblerConfig


class J1Assembler(Transformer):
    def __init__(self, debug: bool = False):
        super().__init__()
        self.labels: Dict[str, int] = {}  # label_name -> address
        self.current_address: int = 0
        self.debug: bool = debug
        self.current_file: str = "<unknown>"
        self.source_lines: List[str] = []
        self.include_stack: List[IncludeStack] = []

        # Dict to store metadata for instructions
        # Key: bytecode word address
        # Value: InstructionMetadata object
        self.instruction_metadata: Dict[int, InstructionMetadata] = {}

        # Dict to store metadata for labels
        # Key: bytecode word address
        # Value: InstructionMetadata object (of type LABEL)
        self.label_metadata: Dict[int, InstructionMetadata] = {}

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

        # Add config instance
        self.config = AssemblerConfig(debug=debug)

    def parse(self, source: str, filename: str = "<unknown>") -> Tree:
        """Parse source code with optional filename for error reporting."""
        self.current_file = filename
        self.macro_processor.set_current_file(filename)  # Add this line
        # Store source lines for listing generation, removing trailing whitespace
        self.source_lines = [line.rstrip() for line in source.splitlines()]
        logging.getLogger("lark").setLevel(logging.DEBUG)
        tree = self.parser.parse(source)

        # print out the tree
        self.logger.debug(tree.pretty())

        self.logger.debug("\n=== Tokens ===")
        if self.debug:
            # Output all tokens in the tree
            for token in tree.scan_values(lambda v: isinstance(v, Token)):
                self.logger.debug(f"Token: {token.type} = '{token.value}'")

        return tree

    def program(
        self, statements: List[Union[InstructionMetadata, List[InstructionMetadata]]]
    ) -> List[int]:
        """Process all statements and resolve labels."""
        self.current_address = 0
        instructions = []

        # First pass: collect labels and flatten instructions
        for stmt in statements:
            self.logger.debug(f"Statement: {stmt}")

            if isinstance(stmt, InstructionMetadata):
                if stmt.type == InstructionType.LABEL:
                    # Check if label is already defined
                    if stmt.label_name in self.labels:
                        raise ValueError(
                            f"{self.current_file}:{stmt.line}:{stmt.column}: "
                            f"Duplicate label: {stmt.label_name}"
                        )
                    # Record label information in both dictionaries
                    addr = len(instructions)
                    self.labels[stmt.label_name] = addr
                    self.label_metadata[addr] = stmt
                    continue  # Skip to next statement

                elif stmt.type == InstructionType.MACRO_DEF:
                    continue  # Skip macro definitions

                else:
                    # Regular instruction
                    addr = len(instructions)
                    self.instruction_metadata[addr] = stmt
                    instructions.append(stmt)

            elif isinstance(stmt, list):
                # Handle macro expansions - each item in the list should be InstructionMetadata
                for macro_inst in stmt:
                    if not isinstance(macro_inst, InstructionMetadata):
                        raise ValueError(
                            f"{self.current_file}: Expected InstructionMetadata in macro expansion, got {type(macro_inst)}"
                        )
                    self.instruction_metadata[len(instructions)] = macro_inst
                    instructions.append(macro_inst)

            else:
                raise ValueError(f"Unexpected statement type: {type(stmt)}")

        self.logger.debug(f"\nCollected labels: {self.labels}")
        self.logger.debug(f"Instructions: {instructions}")

        # Second pass: resolve labels and generate final bytecode
        self.instructions = []
        for inst in instructions:
            if not isinstance(inst, InstructionMetadata):
                raise ValueError(f"Expected InstructionMetadata, got {type(inst)}")

            if inst.type == InstructionType.JUMP:
                # Resolve label reference
                if not inst.label_name:
                    raise ValueError(f"Jump instruction missing label name")
                if inst.label_name not in self.labels:
                    raise ValueError(
                        f"{self.current_file}:{inst.line}:{inst.column}: "
                        f"Undefined label: {inst.label_name}"
                    )
                target = self.labels[inst.label_name]
                self.instructions.append(inst.value | target)
            else:
                self.instructions.append(inst.value)

        self.is_assembled = True
        return self.instructions

    def statement(
        self, items: List[Union[InstructionMetadata, Tuple[str, str]]]
    ) -> Union[InstructionMetadata, List[InstructionMetadata]]:
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

    def jump_op(self, items: List[Token]) -> InstructionMetadata:
        """Handle jump operations with their labels."""
        token = items[0]  # JMP token
        op = str(token)
        label_token = items[1]  # Label token
        label_name = str(label_token)  # Just use the label name directly

        # Create instruction text by combining op and label
        instr_text = f"{op} {label_name}"

        return InstructionMetadata.from_token(
            inst_type=InstructionType.JUMP,
            value=JUMP_OPS[op],  # Base jump opcode
            token=token,
            filename=self.current_file,
            source_lines=self.source_lines,
            label_name=label_name,
            instr_text=instr_text,  # Add instruction text
        )

    def instruction(
        self, items: List[Union[InstructionMetadata, List[InstructionMetadata], Tuple]]
    ) -> Union[InstructionMetadata, List[InstructionMetadata]]:
        """Handles the 'instruction' rule."""
        item = items[0]

        self.logger.debug(f"Processing instruction item: {item}")

        # Handle case where we get a list of instructions (from macro expansion)
        if isinstance(item, list):
            return item  # Pass through list of instructions unchanged

        # Handle InstructionMetadata directly
        if isinstance(item, InstructionMetadata):
            return item

        # For backwards compatibility or special cases (like labels)
        if isinstance(item, tuple):
            item_type, value = item
            if item_type == "label":
                return item  # Pass through labels unchanged
            if item_type == "jump":
                return item  # Pass through jump instructions
            if item_type == "macro_call":
                macro_name = value[0]
                if not self.macro_processor.is_macro(macro_name):
                    raise ValueError(
                        f"{self.current_file}:{token.line}:{token.column}: "
                        f"Unknown macro: {macro_name}"
                    )
                return self.macro_processor.expand_macro(macro_name, value[1])

        raise ValueError(f"Unexpected instruction format: {type(item)}")

    def modifier(self, items: List[Token]) -> Modifier:
        """Convert modifiers into their machine code representation with type."""
        token = items[0]
        mod = str(token)
        self.logger.debug(f"\nModifier: processing '{mod}'")

        if mod in STACK_EFFECTS:
            value = STACK_EFFECTS[mod]
        elif mod in D_EFFECTS:
            value = D_EFFECTS[mod]
        elif mod in R_EFFECTS:
            value = R_EFFECTS[mod]
        else:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Unknown modifier: {mod}"
            )

        self.logger.debug(f"Modifier result: value={value:04x}, text={mod}")
        return Modifier(value=value, text=mod, token=token)

    def modifier_list(self, items: List[Union[Modifier, Token]]) -> ModifierList:
        """Combines all modifiers into a single ModifierList."""
        self.logger.debug(f"\nModifier list items: {items}")

        result_value = 0
        texts = []
        tokens = []

        for item in items:
            if isinstance(item, Token) and item.type == "COMMA":
                continue
            elif isinstance(item, Modifier):
                result_value |= item.value
                texts.append(item.text)
                tokens.append(item.token)
            else:
                token = item if isinstance(item, Token) else items[0]
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Expected modifier, got {item}"
                )

        return ModifierList(value=result_value, text=",".join(texts), tokens=tokens)

    def modifiers(self, items: List[Union[Token, ModifierList]]) -> ModifierList:
        """Process modifiers within square brackets."""
        self.logger.debug(f"\nModifiers: processing items: {items}")

        # Skip brackets
        modifier_items = items[1:-1]  # Skip '[' and ']'

        # We should receive a single ModifierList from modifier_list()
        if len(modifier_items) != 1 or not isinstance(modifier_items[0], ModifierList):
            raise ValueError(f"Expected single ModifierList, got {modifier_items}")

        modifier_list = modifier_items[0]
        self.logger.debug(
            f"Modifiers result: value={modifier_list.value:04x}, text=[{modifier_list.text}]"
        )

        return modifier_list

    def labelref(self, items: List[Token]) -> str:
        """Convert labelref rule into a string."""
        return str(items[0])  # Just return the label name as a string

    def label(self, items: List[Token]) -> InstructionMetadata:
        """Convert label rule into InstructionMetadata."""
        self.logger.debug(f"\nLabel items: {items}")
        token = items[0]  # This is the IDENT token
        label_name = str(token)

        # Create instruction text with colon
        instr_text = f"{label_name}:"

        return InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,  # Labels don't have a value
            token=token,
            filename=self.current_file,
            source_lines=self.source_lines,
            label_name=label_name,
            instr_text=instr_text,  # Add instruction text
        )

    def number(self, items: List[Token]) -> InstructionMetadata:
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
            return InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=machine_code,
                token=token,
                filename=self.current_file,
                source_lines=self.source_lines,
                instr_text=str(token),  # Use token string directly
            )
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
            return InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=machine_code,
                token=token,
                filename=self.current_file,
                source_lines=self.source_lines,
                instr_text=str(token),  # Use token string directly
            )
        else:
            raise ValueError(f"Unknown number format: {token}")

    def basic_alu(self, items: List[Token]) -> Token:
        """Convert basic_alu rule into its token."""
        # items[0] is the Token for the ALU operation
        return items[0]

    def alu_op(self, items: List[Union[Token, ModifierList]]) -> InstructionMetadata:
        """Convert ALU operations into their machine code representation."""
        token = items[0]  # This is the basic ALU operation token
        base_op = str(token)
        modifier_value = 0

        # Get the base ALU operation code
        if base_op not in ALU_OPS:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Unknown ALU operation '{base_op}'"
            )

        # Process modifiers if present
        instr_text = base_op
        if len(items) > 1 and isinstance(items[1], ModifierList):
            modifier_list = items[1]
            modifier_value = modifier_list.value
            instr_text = f"{base_op}[{modifier_list.text}]"

        # Combine all parts of the instruction
        result = ALU_OPS[base_op] | modifier_value | INST_TYPES["alu"]

        return InstructionMetadata.from_token(
            inst_type=InstructionType.BYTE_CODE,
            value=result,
            token=token,
            filename=self.current_file,
            source_lines=self.source_lines,
            instr_text=instr_text,
        )

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
        self, addr: int, code: int, metadata: InstructionMetadata
    ) -> str:
        """Generate a single line for the listing file with explicit field spacing."""
        # Define spacing constants
        addr_space = " " * 5  # After address
        mcode_space = " " * 10  # After machine code
        line_num_space = " " * 2  # After line:col
        source_space = " " * 4  # Before source code
        comment_space = " " * 2  # Before comment
        indent = " " * 2  # Indentation for code under labels

        # Get comment from original source line
        comment_part = ""
        if "//" in metadata.source_line:
            _, comment_part = metadata.source_line.split("//", 1)
            comment_part = comment_part.strip()

        # Add macro annotation to comment if from macro
        if metadata.macro_name:
            macro_note = f"(macro: {metadata.macro_name})"
            if comment_part:
                comment_part = f"{macro_note} {comment_part}"
            else:
                comment_part = macro_note

        # Format line:col with fixed width
        line_col = f"{metadata.line:3d}:{metadata.column:<3d}"

        # Use instr_text for the instruction display
        code_part = metadata.instr_text
        if metadata.type != InstructionType.LABEL:
            code_part = f"{indent}{code_part}"

        # Format the line with explicit spacing
        if metadata.type == InstructionType.LABEL:
            return (
                f"{addr:04x}{addr_space}----{mcode_space}"
                f"{line_col}{line_num_space}"
                f"{code_part:<30}{indent}"
                f"{comment_space}//{comment_space}{comment_part if comment_part else ''}\n"
            )
        else:
            return (
                f"{addr:04x}{addr_space}{code:04x}{mcode_space}"
                f"{line_col}{line_num_space}"
                f"{code_part:<32}"
                f"{comment_space}//{comment_space}{comment_part if comment_part else ''}\n"
            )

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
                # First check if there's a label at this address
                if addr in self.label_metadata:
                    label_info = self.label_metadata[addr]
                    line = self.generate_listing_line(addr, 0, label_info)
                    f.write(line)

                # Then write the instruction
                if addr in self.instruction_metadata:
                    inst_info = self.instruction_metadata[addr]
                    line = self.generate_listing_line(addr, code, inst_info)
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

        # Create instruction text for the macro definition
        # Include stack effect comment if present
        stack_effect = ""
        for item in items:
            if isinstance(item, Token) and item.type == "STACK_COMMENT":
                stack_effect = f" {str(item)}"
                break

        instr_text = f"macro: {macro_name}{stack_effect}"

        # Return InstructionMetadata instead of tuple
        return InstructionMetadata.from_token(
            inst_type=InstructionType.MACRO_DEF,
            value=0,  # No machine code value needed for macro definition
            token=name_token,
            filename=self.current_file,
            source_lines=self.source_lines,
            instr_text=instr_text,  # Add formatted instruction text
            macro_name=macro_name,
        )

    def macro_call(self, items):
        """Handle macro invocations."""
        token = items[0]
        macro_name = str(token)

        # Get expanded instructions directly
        return self.macro_processor.expand_macro(macro_name, token)

    def include_stmt(self, items: List[Token]) -> List[InstructionMetadata]:
        """Process an include statement and return an empty list."""
        token = items[1]
        filename = str(token)[1:-1]  # Remove quotes

        try:
            # Use config to resolve include file
            resolved_path = self.config.resolve_include(
                filename, Path(self.current_file).parent
            )

            if resolved_path is None:
                raise FileNotFoundError(f"Include file not found: {filename}")

            # Save current state
            include_stack_entry = IncludeStack(
                filename=self.current_file,
                line_number=token.line,
                source_lines=self.source_lines,
            )

            # Read the included file using the resolved path
            with open(
                resolved_path, "r"
            ) as f:  # Changed from filename to resolved_path
                included_source = f.read()
                included_lines = [
                    line.rstrip() for line in included_source.splitlines()
                ]

            # Parse and process the included file
            self.logger.debug(
                f"Processing include file: {resolved_path}"
            )  # Updated log message

            # Save current state to stack
            self.include_stack.append(include_stack_entry)

            # Set new current state
            self.current_file = str(resolved_path)  # Use resolved path as current file
            self.source_lines = included_lines

            # Parse and process the included file
            tree = self.parser.parse(included_source)
            self.transform(tree)

            # Restore previous state
            prev_state = self.include_stack.pop()
            self.current_file = prev_state.filename
            self.source_lines = prev_state.source_lines

            # Return empty list since include itself doesn't generate instructions
            return []

        except Exception as e:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Error processing include file {filename}: {str(e)}"
            )

    def format_include_trace(self) -> str:
        """Format the include stack for error messages."""
        if not self.include_stack:
            return ""

        trace = []
        for entry in reversed(self.include_stack):
            trace.append(f"Included from {entry.filename}:{entry.line_number}")
        return "\n".join(trace)


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option(
    "-o", "--output", type=click.Path(), help="Output file (default: aout.hex)"
)
@click.option("-d", "--debug", is_flag=True, help="Enable debug output")
@click.option("--symbols", is_flag=True, help="Generate symbol file (.sym)")
@click.option("--listing", is_flag=True, help="Generate listing file (.lst)")
@click.option(
    "-I",
    "--include",
    multiple=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Add directory to include search path",
)
@click.option("--no-stdlib", is_flag=True, help="Disable standard library include path")
def main(input, output, debug, symbols, listing, include, no_stdlib):
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

        # Configure include paths
        for path in include:
            assembler.config.add_include_path(path)

        if no_stdlib:
            assembler.config.disable_stdlib()

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
