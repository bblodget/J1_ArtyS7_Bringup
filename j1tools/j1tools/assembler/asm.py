#!/usr/bin/env python

import sys
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
    HIGH_LEVEL_WORDS,
)


class J1Assembler(Transformer):
    def __init__(self, debug=False):
        super().__init__()
        self.labels = {}
        self.current_address = 0
        self.debug = debug
        self.current_file = "<unknown>"

        # Load the grammar
        grammar_path = Path(__file__).parent / "j1.lark"
        if not grammar_path.exists():
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}")

        try:
            self.parser = Lark.open(grammar_path, start="start")
            if self.debug:
                print(f"Loaded grammar from {grammar_path}", file=sys.stderr)
        except Exception as e:
            raise Exception(f"Failed to load grammar: {e}")

    def parse(self, source, filename="<unknown>"):
        """Parse source code with optional filename for error reporting."""
        self.current_file = filename
        tree = self.parser.parse(source)
        if self.debug:
            print("\n=== Tokens ===")
            # Print all tokens in the tree
            for token in tree.scan_values(lambda v: isinstance(v, Token)):
                print(f"Token: {token.type} = '{token.value}'")
        return tree

    def program(self, statements):
        # First pass: collect labels
        self.current_address = 0
        instructions = []

        # if self.debug:
        #    print("\n=== Parse Tree ===")
        #    for i, stmt in enumerate(statements):
        #        print(f"Statement {i}: type={type(stmt)}, value={stmt}")

        for stmt in statements:
            if isinstance(stmt, tuple):
                if stmt[0] == "label":
                    if self.debug:
                        print(f"\nProcessing label at {self.current_address}")
                        print(f"Label: {stmt}")
                    if stmt[1] in self.labels:
                        token = stmt[2] if len(stmt) > 2 else None
                        if token:
                            raise ValueError(
                                f"{self.current_file}:{token.line}:{token.column}: "
                                f"Duplicate label: {stmt[1]}"
                            )
                        else:
                            raise ValueError(f"Duplicate label: {stmt[1]}")
                    self.labels[stmt[1]] = self.current_address
                else:
                    # if self.debug:
                    #    print(f"\nProcessing instruction at {self.current_address}")
                    #    print(f"Instruction: {stmt}")
                    #    print(f"Current instructions: {instructions}")
                    self.current_address += 1
                    instructions.append(stmt)

        # if self.debug:
        #    print("\n=== Second Pass ===")
        #    print(f"Labels collected: {self.labels}")
        #    print(f"Instructions to resolve: {instructions}")

        # Second pass: resolve labels and convert to final bytecode
        resolved = []
        for inst in instructions:
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

        return resolved

    def statement(self, items):
        """
        Handles the 'statement' rule by returning the transformed child.
        """
        return items[0]

    def jump_op(self, items):
        """Handle jump operations with their labels."""
        jump_codes = {
            "JMP": 0x0000,
            "ZJMP": 0x2000,
            "CALL": 0x4000,
        }
        op = str(items[0])
        label_type, label = items[1]  # Should be ("label", label_name)
        if op not in jump_codes:
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
            (jump_codes[op], label, items[0]),
        )  # Include token for error reporting

    def instruction(self, items):
        """Handles the 'instruction' rule."""
        item = items[0]

        if self.debug:
            print(f"Processing instruction item: {item}")

        # Handle single instructions
        item_type, value = item
        token = item[2] if len(item) > 2 else None

        if self.debug:
            if item_type == "literal" or item_type == "byte_code":
                print(f"Processing instruction: {item_type} {hex(value)}")
            else:
                print(f"Processing instruction: {item_type} {value}")

        if item_type == "literal":
            return ("byte_code", value)
        elif item_type == "label":
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
        if mod in STACK_EFFECTS:
            return ("modifier", STACK_EFFECTS[mod])
        elif mod in D_EFFECTS:
            return ("modifier", D_EFFECTS[mod])
        elif mod in R_EFFECTS:
            return ("modifier", R_EFFECTS[mod])
        else:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: "
                f"Unknown modifier: {mod}"
            )

    def modifier_list(self, items):
        """Combines all modifiers into a single integer using bitwise OR."""
        result = 0
        for item in items:
            if isinstance(item, tuple) and item[0] == "modifier":
                result |= item[1]
            else:
                token = item if isinstance(item, Token) else items[0]
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Expected modifier, got {item}"
                )
        return ("modifier", result)

    def modifiers(self, items):
        # 0:LBracket, 1:value, 2:RBracket
        return items[1]

    def labelref(self, items):
        return ("label", str(items[0]))

    def label(self, items):
        return ("label", str(items[0]))

    def number(self, items):
        """Convert number tokens to their machine code representation."""
        token = items[0]
        if token.type == "HEX":
            value = int(str(token)[2:], 16)
            # For hex literals, allow full 16-bit range but ensure high bit is set
            return ("literal", value | 0x8000)
        elif token.type == "DECIMAL":
            value = int(str(token)[1:], 10)
            if value < 0:
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Negative numbers must be constructed manually using: "
                    f"#ABS 1- INVERT"
                )
            # For decimal literals, ensure value fits in 15 bits
            if value > 0x7FFF:
                raise ValueError(
                    f"{self.current_file}:{token.line}:{token.column}: "
                    f"Decimal number {value} out of range (0 to 32767)"
                )
            return ("literal", 0x8000 | value)
        else:
            raise ValueError(f"Unknown number format: {token}")

    def stack_words(self, items):
        stack_codes = {
            "DUP": 0x6000 | 0x0001,  # T    [d+1]
            "DROP": 0x6100 | 0x0003,  # N    [d-1]
            "SWAP": 0x6100 | 0x0010,  # N    [T->N]
            "OVER": 0x6100 | 0x0011,  # N    [T->N,d+1]
            "NIP": 0x6000 | 0x0003,  # T    [d-1]
            "NOOP": 0x6000 | 0x0000,  # T    []
            ">R": 0x6100 | 0x0020 | 0x0004 | 0x0003,  # N [T->R,r+1,d-1]
            "R>": 0x6B00 | 0x0010 | 0x000C | 0x0001,  # rT [T->N,r-1,d+1]
            "R@": 0x6B00 | 0x0010 | 0x0001,  # rT [T->N,d+1]
        }
        op = str(items[0])
        if op not in stack_codes:
            raise ValueError(f"Unknown stack operation: {op}")
        return ("byte_code", stack_codes[op])

    def arith_words(self, items):
        """Convert high-level arithmetic words into their machine code representation."""
        op = str(items[0])
        has_ret = len(items) > 1 and str(items[1]) == "+RET"

        # Construct the operation name with optional RET suffix
        full_op = f"{op}+RET" if has_ret else op

        if full_op not in HIGH_LEVEL_WORDS:
            raise ValueError(f"Unknown arithmetic operation: {full_op}")

        return ("byte_code", HIGH_LEVEL_WORDS[full_op])

    def alu_op(self, items):
        """
        Convert ALU operations into their machine code representation.
        Handles both the ALU operation and any modifiers.
        """
        if self.debug:
            print(f"\nALU Operation:")
            print(f"Items: {items}")
            print(f"Current address: {self.current_address}")

        # Extract operation and modifiers
        token = items[0]  # Keep the token object for error reporting
        base_op = str(token)
        modifiers = 0

        # Process any modifiers after the operation
        if len(items) > 1:
            for item in items[1:]:
                if isinstance(item, tuple) and item[0] == "modifier":
                    modifiers |= item[1]
                else:
                    raise ValueError(
                        f"{self.current_file}:{token.line}:{token.column}: Expected modifier, got {item}"
                    )

        # Get the base ALU operation code
        if base_op not in ALU_OPS:
            raise ValueError(
                f"{self.current_file}:{token.line}:{token.column}: Unknown ALU operation '{base_op}'"
            )
        result = ALU_OPS[base_op]

        # Add any modifiers
        result |= modifiers

        return ("byte_code", INST_TYPES["alu"] | result)


def main():
    parser = argparse.ArgumentParser(description="J1 Forth CPU Assembler")
    parser.add_argument("input", help="Input assembly file")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )
    args = parser.parse_args()

    try:
        # Read the input file
        with open(args.input, "r") as f:
            source = f.read()
            if args.debug:
                print(f"Source code:\n{source}", file=sys.stderr)

        if args.debug:
            print("Parsing source...", file=sys.stderr)

        assembler = J1Assembler(debug=args.debug)
        try:
            tree = assembler.parse(source, filename=args.input)
            instructions = assembler.transform(tree)

            # Output hex format
            for inst in instructions:
                print(f"{inst:04x}")

        except lark.exceptions.UnexpectedInput as e:
            # Format Lark's parsing errors to match our style
            # Remove the redundant line/column info from the error message
            error_msg = str(e)
            if ", at line" in error_msg:
                error_msg = error_msg.split(", at line")[0]

            # Find the actual line with the error by counting non-empty, non-comment lines
            real_line = 0
            source_lines = source.splitlines()
            for i, line in enumerate(source_lines[: e.line - 1], 1):
                stripped = line.strip()
                if stripped and not stripped.startswith(";"):
                    real_line = i

            # Get the actual error line for context display
            error_line = source_lines[real_line - 1]
            context = f"\n    {error_line}\n    {' ' * (e.column-1)}^"

            print(
                f"Error: {args.input}:{real_line}:{e.column}: {error_msg}",
                file=sys.stderr,
            )
            if args.debug:
                print(context, file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
