import os
import pytest
from pathlib import Path

from j1tools.assembler.asm import J1Assembler
from lark import Token


class MockItem:
    """Mock item for testing directives"""

    def __init__(self, type_str, value):
        self.type = type_str
        self.value = value

    def __str__(self):
        return self.value


def test_define_decimal_constant():
    """Test defining a decimal constant"""
    assembler = J1Assembler(debug=False)

    # Create a mock decimal item (STACK_DECIMAL)
    value_item = MockItem("STACK_DECIMAL", "42")

    # Manually call the define_directive method
    items = [".define", "ANSWER", value_item]
    assembler.define_directive(items)

    # Check constant is defined with correct value
    assert "ANSWER" in assembler.directives.constants
    assert assembler.directives.constants["ANSWER"] == 42


def test_define_hex_constant():
    """Test defining a hex constant"""
    assembler = J1Assembler(debug=False)

    # Create a mock hex item (STACK_HEX)
    value_item = MockItem("STACK_HEX", "$2A")

    # Manually call the define_directive method
    items = [".define", "ANSWER_HEX", value_item]
    assembler.define_directive(items)

    # Check constant is defined with correct value
    assert "ANSWER_HEX" in assembler.directives.constants
    assert assembler.directives.constants["ANSWER_HEX"] == 42


def test_define_char_constant():
    """Test defining a character constant"""
    assembler = J1Assembler(debug=False)

    # Create a mock char item (STACK_CHAR)
    value_item = MockItem("STACK_CHAR", "'A'")

    # Manually call the define_directive method
    items = [".define", "ASCII_A", value_item]
    assembler.define_directive(items)

    # Check constant is defined with correct value
    assert "ASCII_A" in assembler.directives.constants
    assert assembler.directives.constants["ASCII_A"] == 65  # ASCII value for 'A'


def test_reference_existing_constant():
    """Test referencing an existing constant"""
    assembler = J1Assembler(debug=False)

    # First define a constant
    value_item1 = MockItem("STACK_DECIMAL", "42")
    items1 = [".define", "ANSWER", value_item1]
    assembler.define_directive(items1)

    # Then define another constant referencing the first
    value_item2 = MockItem("IDENT", "ANSWER")
    items2 = [".define", "ALSO_ANSWER", value_item2]
    assembler.define_directive(items2)

    # Check both constants are defined with correct values
    assert "ANSWER" in assembler.directives.constants
    assert assembler.directives.constants["ANSWER"] == 42
    assert "ALSO_ANSWER" in assembler.directives.constants
    assert assembler.directives.constants["ALSO_ANSWER"] == 42


def test_reference_undefined_constant():
    """Test error when referencing an undefined constant"""
    assembler = J1Assembler(debug=False)

    # Try to define a constant referencing an undefined one
    value_item = MockItem("IDENT", "UNDEFINED")
    items = [".define", "BAD_REF", value_item]

    # Should raise ValueError
    with pytest.raises(
        ValueError, match="Referenced constant or label 'UNDEFINED' is not defined"
    ):
        assembler.define_directive(items)


def test_expression_evaluation():
    """Test the expression evaluation function"""
    assembler = J1Assembler(debug=False)

    # Define some constants
    assembler.directives.constants["A"] = 10
    assembler.directives.constants["B"] = 5

    # Test basic arithmetic
    assert assembler.directives.evaluate_expression("A + B") == 15
    assert assembler.directives.evaluate_expression("A - B") == 5
    assert assembler.directives.evaluate_expression("A * B") == 50
    assert assembler.directives.evaluate_expression("A / B") == 2

    # Test bitwise operations
    assert assembler.directives.evaluate_expression("A & B") == 0
    assert assembler.directives.evaluate_expression("A | B") == 15
    assert assembler.directives.evaluate_expression("A ^ B") == 15

    # Test comparisons
    assert assembler.directives.evaluate_expression("A == B") == 0
    assert assembler.directives.evaluate_expression("A != B") == 1
    assert assembler.directives.evaluate_expression("A > B") == 1
    assert assembler.directives.evaluate_expression("A < B") == 0

    # Test complex expression
    assert assembler.directives.evaluate_expression("(A + B) * (A - B)") == 75


def test_expression_with_undefined_constant():
    """Test error when evaluating expression with undefined constant"""
    assembler = J1Assembler(debug=False)

    # Define some constants
    assembler.directives.constants["A"] = 10

    # Should raise ValueError for undefined constant
    with pytest.raises(ValueError, match="Undefined constant: C"):
        assembler.directives.evaluate_expression("A + C")


def test_constant_exists():
    """Test the constant_exists function"""
    assembler = J1Assembler(debug=False)

    # Define a constant
    assembler.directives.constants["TEST"] = 42

    # Check exists returns correct values
    assert assembler.directives.constant_exists("TEST") == True
    assert assembler.directives.constant_exists("UNDEFINED") == False
