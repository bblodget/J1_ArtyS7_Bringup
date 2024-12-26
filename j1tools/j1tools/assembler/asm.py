#!/usr/bin/env python

import sys
import argparse
from lark import Lark, Transformer, Tree, Token
from pathlib import Path


class J1Assembler:
    def __init__(self, debug=False):
        self.debug = debug
        # Load grammar
        grammar_path = Path(__file__).parent / "j1.lark"
        with open(grammar_path) as f:
            self.parser = Lark(
                f.read(), parser="earley", debug=self.debug, ambiguity="explicit"
            )

        # Instruction encodings
        self.opcodes = {
            # Basic Stack Operations
            "NOP": 0x6000,  # T alu
            "DUP": 0x6011,  # T T->N d+1 alu
            "DROP": 0x6103,  # N d-1 alu
            "OVER": 0x6101,  # N T->N d+1 alu
            "SWAP": 0x6111,  # N T->N alu
            # Stack Manipulation
            ">R": 0x6024,  # N T->R r+1 d-1 alu
            "R>": 0x6B01,  # rT T->N r-1 d+1 alu
            "R@": 0x6B01,  # rT T->N d+1 alu
            # Memory & I/O
            "@": 0x6900,  # mem[T] alu
            "!": 0x6032,  # N->[T] d-2 alu
            "IO@": 0x6D50,  # io[T] IORD alu
            "IO!": 0x6042,  # N->io[T] d-2 alu
            # ALU Operations
            "+": 0x6203,  # T+N d-1 alu
            # Control Flow
            "RET": 0x6080,  # Return (T RET r-1 alu)
        }

    def assemble_line(self, tree):
        if self.debug:
            print(f"Processing instruction: {tree}", file=sys.stderr)

        if tree.data == "instruction":
            # Handle LIT instruction
            if (
                len(tree.children) == 2
                and isinstance(tree.children[0], Token)
                and tree.children[0].value == "LIT"
            ):
                value = int(tree.children[1].children[1].value)
                if self.debug:
                    print(f"LIT value: {value}", file=sys.stderr)
                return 0x8000 | (value & 0x7FFF)

            # Handle other instructions
            opcode = tree.children[0].value
            if opcode in self.opcodes:
                return self.opcodes[opcode]
            else:
                raise ValueError(f"Unknown opcode: {opcode}")
        return None

    def assemble(self, source):
        # Parse source
        tree = self.parser.parse(source)

        if self.debug:
            try:
                print(f"Parse tree:\n{tree.pretty()}", file=sys.stderr)
            except Exception as e:
                print(f"Error printing parse tree: {e}", file=sys.stderr)
                print(f"Raw tree: {tree}", file=sys.stderr)

        # First pass - collect labels
        self.labels = {}
        addr = 0
        for line in tree.children:
            if line.children:  # Skip empty lines
                child = line.children[0]
                if isinstance(child, Tree):  # Check if it's a Tree node
                    if child.data == "label":
                        self.labels[child.children[0].value] = addr
                    elif child.data == "instruction":
                        addr += 1

        # Second pass - generate code
        code = []
        for line in tree.children:
            if line.children:  # Skip empty lines
                child = line.children[0]
                if isinstance(child, Tree) and child.data == "instruction":
                    if instr := self.assemble_line(child):
                        code.append(instr)

        return code


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

        asm = J1Assembler(debug=args.debug)

        if args.debug:
            print("Parsing source...", file=sys.stderr)

        code = asm.assemble(source)

        if args.debug:
            print(f"Labels found: {asm.labels}", file=sys.stderr)
            print(f"Generated {len(code)} instructions", file=sys.stderr)

        # Output hex format
        for word in code:
            print(f"{word:04X}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
