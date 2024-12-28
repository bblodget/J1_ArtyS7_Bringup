from lark import Lark, Transformer
from lark.lexer import Token


class J1Transformer(Transformer):
    def __init__(self):
        super().__init__()
        self.labels = {}
        self.current_address = 0

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
        print(f"instruction: items={items}, types={[type(x) for x in items]}")
        if len(items) == 2 and items[0] == "LIT":
            number = items[1]
            print(f"LIT number={number}, type={type(number)}")
            return 0x8000 | number
        elif items[0] == "+":
            return 0x6203
        elif items[0] == "RET":
            return 0x6080
        elif items[0] == "CALL":
            return ("call", items[1])
        elif items[0] == "JMP":
            return ("jump", items[1])
        else:
            raise ValueError(f"Unknown instruction: {items}")

    def HEX(self, token):
        print(f"HEX: token={token}")
        # Remove '#$' prefix and convert to integer
        return int(str(token)[2:], 16)

    def DECIMAL(self, token):
        print(f"DECIMAL: token={token}")
        # Remove '#' prefix and convert to integer
        return int(str(token)[1:], 10)

    def IDENT(self, token):
        print(f"IDENT: token={token}")
        return str(token)

    def label(self, items):
        # Return tuple marking this as a label
        label_name = items[0]
        print(f"label: {label_name}")
        return ("label", label_name)

    def labelref(self, items):
        # Return the identifier for the label reference
        return items[0]


# Create the parser
parser = Lark.open("j1.lark")

# Test program
test_program = """
; Simple test program with hex and decimal numbers
start:
    LIT #$2A        ; Push hex 2A (decimal 42)
    LIT #10         ; Push decimal 10
    +               ; Add them together
    RET            ; Return
"""

# Parse and transform the program
tree = parser.parse(test_program)
transformer = J1Transformer()
instructions = transformer.transform(tree)

# Print the bytecode in hexadecimal
print("\nBytecode:")
for i, inst in enumerate(instructions):
    print(f"{i:04x}: {inst:04x}")
