#!/usr/bin/env python

import sys
import argparse
from lark import Lark, Transformer, Tree, Token
from pathlib import Path


class J1Assembler(Transformer):
    def __init__(self, debug=False):
        super().__init__()
        self.labels = {}
        self.current_address = 0
        self.debug = debug

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

    def parse(self, source):
        return self.parser.parse(source)

    def program(self, statements):
        # First pass: collect all labels and their addresses
        self.current_address = 0
        instructions = []

        # Process all statements to collect labels
        for stmt in statements:
            if isinstance(stmt, tuple) and stmt[0] == "label":
                label_name = stmt[1]
                if label_name in self.labels:
                    raise ValueError(f"Duplicate label: {label_name}")
                self.labels[label_name] = self.current_address
            else:
                self.current_address += 1
                if stmt is not None:
                    instructions.append(stmt)

        # Second pass: resolve label references
        resolved_instructions = []
        for inst in instructions:
            if isinstance(inst, tuple) and inst[0] == "jump":
                jump_type, label = inst[1], inst[2]
                if label not in self.labels:
                    raise ValueError(f"Undefined label: {label}")
                target_address = self.labels[label]
                resolved_instructions.append(jump_type | target_address)
            else:
                resolved_instructions.append(inst)

        return resolved_instructions

    def statement(self, items):
        """
        Handles the 'statement' rule by returning the transformed child.
        """
        return items[0]

    def jump_op(self, items):
        jump_codes = {
            "JMP": 0x0000,  # Unconditional jump
            "ZJMP": 0x2000,  # Jump if TOS = 0
            "CALL": 0x4000,  # Call subroutine
        }
        op = str(items[0])
        if op not in jump_codes:
            raise ValueError(f"Unknown jump operation: {op}")
        return jump_codes[op]

    def instruction(self, items):
        if len(items) == 1:
            item = items[0]
            if isinstance(item, int):  # Number literal
                return 0x8000 | item
            elif isinstance(item, str):  # Label reference
                return item
            elif isinstance(item, tuple):
                if item[0] == "alu":  # ALU operation
                    return item[1]  # Return just the operation code
                elif item[0] == "stack_word":  # Stack operation
                    return item[1]  # Return just the operation code
            else:
                raise ValueError(f"Invalid instruction type: {type(item)}")
        elif len(items) == 2:
            if isinstance(items[0], int) and isinstance(items[1], str):
                # It's a jump instruction with labelref
                return ("jump", items[0], items[1])
            else:
                # It's an ALU operation with modifiers
                alu_op, modifiers = items
                if isinstance(alu_op, tuple) and alu_op[0] == "alu":
                    return alu_op[1] | modifiers
                else:
                    raise ValueError(f"Invalid ALU operation with modifiers: {items}")
        else:
            raise ValueError(f"Invalid instruction format: {items}")

    def alu_op(self, items):
        # Base ALU operation codes
        alu_codes = {
            "T": 0x6000,  # T
            "N": 0x6100,  # N
            "T+N": 0x6200,  # Add
            "T-N": 0x6C00,  # Subtract
            "T&N": 0x6300,  # AND
            "T|N": 0x6400,  # OR
            "T^N": 0x6500,  # XOR
            "~T": 0x6600,  # NOT
            "N==T": 0x6700,  # Equal
            "N<T": 0x6800,  # Less than
            "Nu<T": 0x6F00,  # Unsigned less than
            "N<<T": 0x6A00,  # Left shift
            "N>>T": 0x6900,  # Right shift (logical)
            "N>>>T": 0x6900,  # Right shift (arithmetic)
            "1+": 0x6160,  # Increment
            "1-": 0x6170,  # Decrement
        }

        if len(items) == 1:
            op = str(items[0])
        elif len(items) == 2:
            if str(items[0]) == "~":
                op = f"~{items[1]}"
            else:
                op = f"{items[0]}"
        elif len(items) == 3:
            op = f"{items[0]}{items[1]}{items[2]}"
        else:
            raise ValueError(f"Invalid ALU operation format: {items}")

        if op not in alu_codes:
            raise ValueError(f"Unknown ALU operation: {op}")

        # Return tuple indicating this is an ALU operation
        return ("alu", alu_codes[op])

    def modifier(self, items):
        # Stack operation codes
        stack_ops = {
            "T->N": 0x0010,  # Copy T to N
            "T->R": 0x0020,  # Copy T to R
            "N->[T]": 0x0030,  # Memory write
            "N->io[T]": 0x0040,  # I/O write
            "IORD": 0x0050,  # I/O read
            "fDINT": 0x0060,  # Disable interrupts
            "fEINT": 0x0070,  # Enable interrupts
            "RET": 0x0080,  # Return
        }

        # Stack Delta Codes
        stack_d = {"d+0": 0x0, "d+1": 0x1, "d-2": 0x2, "d-1": 0x3}
        stack_r = {"r+0": 0x0, "r+1": 0x4, "r-2": 0x8, "r-1": 0xC}

        mod = str(items[0])
        if mod in stack_ops:
            return stack_ops[mod]
        elif mod in stack_d:
            return stack_d[mod]
        elif mod in stack_r:
            return stack_r[mod]
        else:
            raise ValueError(f"Unknown modifier: {mod}")

    def modifier_list(self, items):
        """
        Combines all modifiers into a single integer using bitwise OR.
        """
        result = 0
        for mod in items:
            result |= mod
        return result

    def modifiers(self, items):
        # 0:LBracket, 1:value, 2:RBracket
        return items[1]

    def labelref(self, items):
        return str(items[0])

    def label(self, items):
        return ("label", str(items[0]))

    def number(self, items):
        token = items[0]
        if token.type == "HEX":
            return int(str(token)[2:], 16)
        elif token.type == "DECIMAL":
            return int(str(token)[1:], 10)
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
        }
        op = str(items[0])
        if op not in stack_codes:
            raise ValueError(f"Unknown stack operation: {op}")
        return ("stack_word", stack_codes[op])


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
        tree = assembler.parse(source)
        instructions = assembler.transform(tree)

        # Output hex format
        for i, inst in enumerate(instructions):
            # print(f"{i:04x}: {inst:04x}")
            print(f"{inst:04x}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
