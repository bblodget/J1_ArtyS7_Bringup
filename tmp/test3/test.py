from lark import Lark, Transformer


class J1Transformer(Transformer):
    def __init__(self):
        super().__init__()
        self.labels = {}
        self.current_address = 0
        self.unresolved_calls = []
        self.unresolved_jumps = []

    def program(self, statements):
        # First pass: collect all labels and their addresses
        self.current_address = 0
        instructions = []

        # Process all statements to collect labels
        for stmt in statements:
            if isinstance(stmt, tuple) and stmt[0] == "label":
                self.labels[stmt[1]] = self.current_address
            else:
                self.current_address += 1
                if stmt is not None:
                    instructions.append(stmt)

        # Second pass: resolve calls and jumps
        resolved_instructions = []
        self.current_address = 0
        for inst in instructions:
            if isinstance(inst, tuple):
                if inst[0] == "call":
                    target = self.labels.get(inst[1])
                    if target is None:
                        raise ValueError(f"Undefined label: {inst[1]}")
                    resolved_instructions.append(0x2000 | target)
                elif inst[0] == "jump":
                    target = self.labels.get(inst[1])
                    if target is None:
                        raise ValueError(f"Undefined label: {inst[1]}")
                    resolved_instructions.append(0x0000 | target)
            else:
                resolved_instructions.append(inst)
            self.current_address += 1

        return resolved_instructions

    def statement(self, items):
        if not items:
            return None
        return items[0]

    def instruction(self, items):
        if len(items) == 2 and items[0] == "LIT":
            # LIT instruction: Convert number and set high bit
            number = int(items[1].replace("#", ""))
            return 0x8000 | number
        elif items[0] == "+":
            # ADD instruction: ALU operation
            return 0x6203
        elif items[0] == "RET":
            # RET instruction
            return 0x6080
        elif items[0] == "CALL":
            # Return tuple for resolution in second pass
            return ("call", items[1])
        elif items[0] == "JMP":
            # Return tuple for resolution in second pass
            return ("jump", items[1])
        else:
            raise ValueError(f"Unknown instruction: {items}")

    def NUMBER(self, token):
        return str(token)

    def LABEL(self, token):
        # Return tuple marking this as a label
        return ("label", str(token).rstrip(":"))


# Create the parser
parser = Lark.open("j1.lark")

# Test program
test_program = """
; Simple test program with subroutine
; Defines an add_one subroutine that adds 1 to top of stack

start:
    LIT #5          ; Push 5 onto stack
    CALL add_one    ; Call our subroutine
    JMP start       ; Loop forever

add_one:
    LIT #1          ; Push 1
    +               ; Add it to previous value
    RET             ; Return to caller
"""

# Parse and transform the program
tree = parser.parse(test_program)
transformer = J1Transformer()
instructions = transformer.transform(tree)

# Print the bytecode in hexadecimal
print("\nBytecode:")
for i, inst in enumerate(instructions):
    print(f"{i:04x}: {inst:04x}")
