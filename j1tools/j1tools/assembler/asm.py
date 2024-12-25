#!/usr/bin/env python

import sys
import argparse


class J1Assembler:
    def __init__(self):
        # Instruction encodings from instructionset-16kb-dualport.fs
        self.opcodes = {
            "NOP": 0x6000,  # T alu
            "DUP": 0x6011,  # T T->N d+1 alu
            "DROP": 0x6103,  # N d-1 alu
            "IO@": 0x6D50,  # io[T] IORD alu
            "IO!": 0x6040,  # N->io[T] alu
            "RET": 0x6080,  # Return from subroutine (T RET r-1 alu)
            "AND": 0x6203,  # N&T d-1 alu
        }
        self.labels = {}
        self.comments = {}  # Store comments for each instruction

    def first_pass(self, lines):
        # Collect label addresses
        addr = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            if line.endswith(":"):  # Label definition
                label = line[:-1].strip()
                self.labels[label] = addr
            else:
                addr += 1

    def assemble_line(self, line):
        # Split line into instruction and comment
        parts = line.split(";", 1)
        instruction = parts[0].strip()
        comment = parts[1].strip() if len(parts) > 1 else ""

        if not instruction or instruction.endswith(":"):
            return None, comment

        # Parse instruction and target
        words = instruction.split()
        opcode = words[0]
        target = words[1] if len(words) > 1 else None

        if opcode == "LIT":
            value = int(target.replace("#", ""), 16)
            code = 0x8000 | value  # LIT
            self.comments[len(self.code)] = f"Push {value:04X}"
        elif opcode == "JMP":
            addr = 0 if target is None else self.labels.get(target, 0)
            code = 0x0000 | (addr & 0x1FFF)  # Jump, target in lower 13 bits
            self.comments[len(self.code)] = f"Jump to {target if target else 'start'}"
        elif opcode == "0BRANCH":
            addr = 0 if target is None else self.labels.get(target, 0)
            code = 0x2000 | (addr & 0x1FFF)  # Conditional jump
            self.comments[len(self.code)] = (
                f"Branch to {target if target else 'start'} if zero"
            )
        elif opcode == "CALL":
            addr = self.labels.get(target, 0)
            code = 0x4000 | (addr & 0x1FFF)  # Call subroutine
            self.comments[len(self.code)] = f"Call subroutine at {target}"
        else:
            code = self.opcodes[opcode]
            self.comments[len(self.code)] = comment

        return code, comment

    def assemble(self, filename):
        self.code = []

        # Read all lines
        with open(filename) as f:
            lines = [line.strip() for line in f]

        # First pass - collect labels
        self.first_pass(lines)

        # Second pass - generate code
        for line in lines:
            if code_comment := self.assemble_line(line):
                code, _ = code_comment
                if code is not None:
                    self.code.append(code)

        return self.code, self.comments


def main():
    parser = argparse.ArgumentParser(description="J1 Forth CPU Assembler")
    parser.add_argument("input", help="Input assembly file")
    args = parser.parse_args()

    asm = J1Assembler()
    code, comments = asm.assemble(args.input)

    # Output hex format with comments
    for i, word in enumerate(code):
        comment = comments.get(i, "")
        print(f"{word:04X}        // {comment}")


if __name__ == "__main__":
    main()
