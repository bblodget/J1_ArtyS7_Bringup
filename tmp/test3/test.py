from lark import Lark

# Create the parser
parser = Lark.open('j1.lark')

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

# Parse the program
tree = parser.parse(test_program)
print(tree.pretty())