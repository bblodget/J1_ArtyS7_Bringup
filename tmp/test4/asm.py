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
            "ZJMP": 0x1000,  # Jump if TOS = 0
            "CALL": 0x2000,  # Call subroutine
        }
        op = str(items[0])
        if op not in jump_codes:
            raise ValueError(f"Unknown jump operation: {op}")
        return jump_codes[op]

    def instruction(self, items):
        if len(items) == 1:
            if isinstance(items[0], int):  # Number literal
                return 0x8000 | items[0]
            else:  # ALU operation without modifiers
                return items[0]
        elif len(items) == 2:
            if isinstance(items[0], int) and isinstance(items[1], str):
                # It's a jump instruction with labelref
                return ("jump", items[0], items[1])
            else:
                # It's an ALU operation with modifiers
                alu_op, modifiers = items
                return alu_op | modifiers
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

        return alu_codes[op]

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


# Create the parser
parser = Lark.open("j1.lark", start="start")

# Test program using subroutine calls and return
test_program = """
; Test program demonstrating subroutine calls
start:                    ; Note the colon after label
    #$2A                 ; Push hex 2A (decimal 42)
    #10                  ; Push decimal 10
    CALL add_nums        ; Call our addition subroutine
    N[d-1]               ; DROP the result
    JMP start            ; Loop forever

add_nums:                ; Note the colon after label
     T+N[d-1]            ; Add top two stack items
     T[T->R]             ; Save result to return stack
     T[RET]                 ; Return to caller
"""

# Parse and transform the program
tree = parser.parse(test_program)
transformer = J1Transformer()
instructions = transformer.transform(tree)

# Print the bytecode in hexadecimal
print("\nBytecode:")
for i, inst in enumerate(instructions):
    if isinstance(inst, int):
        print(f"{i:04x}: {inst:04x}")
    elif isinstance(inst, tuple):
        # Handle jump instructions
        if inst[0] == "jump":
            print(f"{i:04x}: {inst[1]:04x} ; {inst[2]}")
        else:
            print(f"{i:04x}: {inst}")
    else:
        print(f"{i:04x}: {inst}")
