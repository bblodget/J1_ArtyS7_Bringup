#!/usr/bin/env python

import sys
import argparse
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
        # First pass: collect labels
        self.current_address = 0
        instructions = []

        for stmt in statements:
            if isinstance(stmt, tuple):
                if stmt[0] == "label":
                    if stmt[1] in self.labels:
                        raise ValueError(f"Duplicate label: {stmt[1]}")
                    self.labels[stmt[1]] = self.current_address
                else:
                    self.current_address += 1
                    instructions.append(stmt)

        # Second pass: resolve labels and convert to final bytecode
        resolved = []
        for inst in instructions:
            type_, value = inst
            if type_ == "jump":
                jump_type, label = value
                if label not in self.labels:
                    raise ValueError(f"Undefined label: {label}")
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
        """
        Handle jump operations with their labels.
        First item is the jump type, second is the label reference.
        """
        jump_codes = {
            "JMP": 0x0000,
            "ZJMP": 0x2000,
            "CALL": 0x4000,
        }
        op = str(items[0])
        label_type, label = items[1]  # Should be ("label", label_name)
        if op not in jump_codes:
            raise ValueError(f"Unknown jump operation: {op}")
        if label_type != "label":
            raise ValueError(f"Expected label reference, got {label_type}")
        return ("jump", (jump_codes[op], label))

    def instruction(self, items):
        """
        Handles the 'instruction' rule by converting all inputs to either 'byte_code' or 'label'.
        """
        item_type, value = items[0]  # First item is always a typed tuple

        if item_type == "literal":
            return ("byte_code", INST_TYPES["imm"] | value)
        elif item_type == "label":
            return items[0]  # Pass through labels unchanged
        elif item_type == "jump":
            # Don't try to resolve the label yet, just pass it through
            return items[0]  # Pass through jump instructions for later resolution
        elif item_type == "alu":
            result = INST_TYPES["alu"] | value
            # Get modifier if present
            if len(items) > 1:
                mod_type, mod_value = items[1]  # Should be the combined modifier value
                if mod_type == "modifier":
                    result |= mod_value
            return ("byte_code", result)
        elif item_type == "byte_code":
            return items[0]  # Already final form

        raise ValueError(f"Invalid instruction type: {item_type}")

    def modifier(self, items):
        """Convert modifiers into their machine code representation with type."""
        mod = str(items[0])
        if mod in STACK_EFFECTS:
            return ("modifier", STACK_EFFECTS[mod])
        elif mod in D_EFFECTS:
            return ("modifier", D_EFFECTS[mod])
        elif mod in R_EFFECTS:
            return ("modifier", R_EFFECTS[mod])
        else:
            raise ValueError(f"Unknown modifier: {mod}")

    def modifier_list(self, items):
        """
        Combines all modifiers into a single integer using bitwise OR and returns as a typed tuple.
        """
        result = 0
        for mod_type, value in items:
            if mod_type != "modifier":
                raise ValueError(f"Expected modifier, got {mod_type}")
            result |= value
        return ("modifier", result)

    def modifiers(self, items):
        # 0:LBracket, 1:value, 2:RBracket
        return items[1]

    def labelref(self, items):
        return ("label", str(items[0]))

    def label(self, items):
        return ("label", str(items[0]))

    def number(self, items):
        token = items[0]
        if token.type == "HEX":
            value = int(str(token)[2:], 16)
        elif token.type == "DECIMAL":
            value = int(str(token)[1:], 10)
        else:
            raise ValueError(f"Unknown number format: {token}")
        return ("literal", value)

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
        if op not in HIGH_LEVEL_WORDS:
            raise ValueError(f"Unknown arithmetic operation: {op}")
        return ("byte_code", HIGH_LEVEL_WORDS[op])

    def alu_op(self, items):
        """Convert ALU operations into their machine code representation with type."""
        # Build operation string from items
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

        if op in ALU_OPS:
            return ("alu", ALU_OPS[op])

        # Special cases for operations that need stack effects
        if op == "T+N":
            return ("byte_code", INST_TYPES["alu"] | ALU_OPS["T+N"])
        elif op == "T-N":
            return ("byte_code", INST_TYPES["alu"] | ALU_OPS["N-T"])
        elif op == "T&N":
            return ("byte_code", INST_TYPES["alu"] | ALU_OPS["T&N"])
        elif op == "T|N":
            return ("byte_code", INST_TYPES["alu"] | ALU_OPS["T|N"])
        elif op == "T^N":
            return ("byte_code", INST_TYPES["alu"] | ALU_OPS["T^N"])
        elif op == "~T":
            return ("byte_code", INST_TYPES["alu"] | ALU_OPS["~T"])

        raise ValueError(f"Unknown ALU operation: {op}")


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
