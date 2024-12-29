from lark import Lark, Transformer, v_args
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

        # Second pass: resolve labels (if needed)
        resolved_instructions = []
        for inst in instructions:
            resolved_instructions.append(inst)

        return resolved_instructions

    def statement(self, items):
        if not items:
            return None
        return items[0]

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
            "N>>T": 0x6900,  # Right shift
            "N>>>T": 0x6900,  # Arithmetic right shift
            "1+": 0x6160,  # Increment
            "1-": 0x6170,  # Decrement
        }

        # Convert items to operation string
        if len(items) == 1:
            op = str(items[0])
        elif len(items) == 2:
            if items[0] == "~":
                op = f"~{items[1]}"
            else:
                op = f"{items[0]}"
        elif len(items) == 3:
            op = f"{items[0]}{items[1]}{items[2]}"
        else:
            raise ValueError(f"Invalid ALU operation format: {items}")

        # Get base instruction
        instruction = alu_codes.get(op)
        if instruction is None:
            raise ValueError(f"Unknown ALU operation: {op}")

        return instruction

    def modifiers(self, items):
        """
        Handles the 'modifiers' rule by extracting the modifier_list value.
        Expected items: [LBRACKET, modifier_value, RBRACKET]
        """
        if len(items) == 3:
            lbracket, modifier_value, rbracket = items
            if (
                isinstance(lbracket, Token)
                and lbracket.type == "LBRACKET"
                and isinstance(rbracket, Token)
                and rbracket.type == "RBRACKET"
            ):
                return modifier_value
            else:
                raise ValueError("Invalid modifiers format: Missing brackets")
        elif len(items) == 1:
            # In case there are no brackets (though grammatically shouldn't happen)
            return items[0]
        else:
            raise ValueError("Invalid modifiers format")

    def modifier_list(self, items):
        """
        Combines all modifiers into a single integer using bitwise OR.
        """
        # Stack delta encoding
        stack_d = {"d+0": 0x0, "d+1": 0x1, "d-2": 0x2, "d-1": 0x3}
        stack_r = {"r+0": 0x0, "r+1": 0x4, "r-2": 0x8, "r-1": 0xC}
        # Stack operations
        stack_ops = {"T->N": 0x0020, "T->R": 0x0040, "N->[T]": 0x0060}

        result = 0
        for modifier in items:
            if isinstance(modifier, str):
                if modifier in stack_d:
                    result |= stack_d[modifier]
                elif modifier in stack_r:
                    result |= stack_r[modifier]
                elif modifier in stack_ops:
                    result |= stack_ops[modifier]
                else:
                    raise ValueError(f"Unknown modifier: {modifier}")
            else:
                raise ValueError(f"Modifier must be a string: {modifier}")

        return result

    def instruction(self, items):
        if len(items) == 1:
            if isinstance(items[0], int):  # Number literal
                return 0x8000 | items[0]
            else:  # ALU operation without modifiers
                return items[0]
        elif len(items) == 2:  # ALU operation with modifiers
            alu_op, modifiers = items
            if isinstance(alu_op, int) and isinstance(modifiers, int):
                return alu_op | modifiers
            else:
                raise TypeError(
                    f"Invalid types for bitwise OR: {type(alu_op)}, {type(modifiers)}"
                )
        else:
            raise ValueError(f"Invalid instruction format: {items}")

    def HEX(self, token):
        return int(str(token)[2:], 16)

    def DECIMAL(self, token):
        return int(str(token)[1:], 10)

    def IDENT(self, token):
        return str(token)

    def label(self, items):
        return ("label", items[0])

    def labelref(self, items):
        return items[0]

    def number(self, items):
        return items[0]

    def modifier(self, items):
        return str(items[0])


# Create the parser
parser = Lark.open("j1.lark", start="start")

# Test program using new syntax
test_program = """
; Test program demonstrating new ALU operations
start:
    #$2A                    ; Push hex 2A (decimal 42)
    #10                     ; Push decimal 10
    T[T->N,d+1]             ; DUP - Duplicate top of stack
    T+N[d-1]                ; Add them together
    N[d-1]                  ; DROP - Remove top item
"""

# Parse and transform the program
tree = parser.parse(test_program)
transformer = J1Transformer()
instructions = transformer.transform(tree)

# Print the bytecode in hexadecimal
print("\nBytecode:")
for i, inst in enumerate(instructions):
    print(f"{i:04x}: {inst:04x}")
