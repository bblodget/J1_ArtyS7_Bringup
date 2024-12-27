from lark import Lark, Transformer


class J1Transformer(Transformer):
    def program(self, statements):
        # Flatten the list of instructions
        return [inst for inst in statements if inst is not None]

    def statement(self, items):
        # For now, we only return instructions (ignore labels)
        return items[0] if items else None

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
        else:
            raise ValueError(f"Unknown instruction: {items}")

    def NUMBER(self, token):
        return str(token)

    def LABEL(self, token):
        return None  # We'll handle labels in a later version


# Create the parser
parser = Lark.open("j1.lark")

# Test program
test_program = """
; Simple test program
; Pushes two numbers and adds them

start:
    LIT #1      ; Push 1
    LIT #2      ; Push 2
    +           ; Add them
    RET         ; Return
"""

# Parse and transform the program
tree = parser.parse(test_program)
transformer = J1Transformer()
instructions = transformer.transform(tree)

# Print the bytecode in hexadecimal
print("\nBytecode:")
for i, inst in enumerate(instructions):
    print(f"{i:04x}: {inst:04x}")
