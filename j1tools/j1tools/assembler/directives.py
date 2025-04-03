# directives.py

import logging
from typing import List, Dict, Any, Optional, Union
from .asm_types import AssemblerState, InstructionMetadata, InstructionType
import re

class Directives:
    def __init__(self, state: AssemblerState, arch_flags: dict, constants: dict, debug: bool = False):
        self.state = state
        self.arch_flags = arch_flags
        self.constants = constants
        self.logger = logging.getLogger("j1asm.directives")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        # Reference to the assembler for accessing labels
        self.assembler = None

    def set_assembler(self, assembler):
        """Set a reference to the assembler for accessing labels"""
        self.assembler = assembler

    def arch_flag_directive(self, items: List[str]):
        """Handle architecture flag directives like .arch_flag fetch_type dualport"""
        flag_name = str(items[1])
        flag_value = str(items[2])

        if flag_name not in self.arch_flags:
            raise ValueError(f"Unknown architecture flag: {flag_name}")

        if flag_name == "fetch_type":
            if flag_value not in ["quickstore", "dualport", "0", "1"]:
                raise ValueError(f"Invalid value for fetch_type: {flag_value}")
            flag_value = "dualport" if flag_value in ["dualport", "1"] else "quickstore"
            self.constants["ARCH_FETCH_TYPE"] = 1 if flag_value == "dualport" else 0

        elif flag_name == "alu_ops":
            if flag_value not in ["original", "extended", "0", "1"]:
                raise ValueError(f"Invalid value for alu_ops: {flag_value}")
            flag_value = "extended" if flag_value in ["extended", "1"] else "original"
            self.constants["ARCH_ALU_OPS"] = 1 if flag_value == "extended" else 0

        self.arch_flags[flag_name] = flag_value
        self.logger.debug(f"Architecture flag set: {flag_name} = {flag_value}")
        self.logger.debug(f"Constants: ARCH_{flag_name.upper()} = {self.constants[f'ARCH_{flag_name.upper()}']}") 

    def define_directive(self, items: List[Any]) -> Optional[InstructionMetadata]:
        """Handle .define directives that define general constants
        
        Format: .define CONST_NAME value
        where value can be a number (decimal or hex) or another constant
        """
        # Extract constant name and value from items
        const_name = str(items[1])
        value_item = items[2]
        
        # Process the value based on its type
        if hasattr(value_item, 'type') and value_item.type == "IDENT":
            # Reference to another constant or label
            value_name = str(value_item)
            if value_name in self.constants:
                value = self.constants[value_name]
            elif self.assembler and hasattr(self.assembler, 'labels') and value_name in self.assembler.labels:
                # Reference to a label - store the label address
                value = self.assembler.labels[value_name]
            else:
                raise ValueError(f"Referenced constant or label '{value_name}' is not defined")
        elif hasattr(value_item, 'type') and value_item.type == "STACK_HEX":
            # Hex value (remove $ prefix)
            value = int(str(value_item)[1:], 16)
        elif hasattr(value_item, 'type') and value_item.type == "STACK_DECIMAL":
            # Decimal value
            value = int(str(value_item), 10)
        elif hasattr(value_item, 'type') and value_item.type == "STACK_CHAR":
            # Character value
            token_str = str(value_item)
            if len(token_str) != 3:
                raise ValueError(f"Invalid character constant: {token_str}")
            value = ord(token_str[1])
        else:
            # Try to interpret as a raw value
            try:
                value = int(str(value_item), 0)
            except ValueError:
                raise ValueError(f"Invalid constant value: {value_item}")
        
        # Store the constant in the constants dictionary
        self.constants[const_name] = value
        self.logger.debug(f"Defined constant: {const_name} = {value}")
        
        # Return appropriate InstructionMetadata for listing
        if hasattr(value_item, 'token'):
            token = value_item.token
        elif hasattr(value_item, 'line'):
            token = value_item
        else:
            token = None
            
        # Don't return instruction metadata as this is a directive, not actual code
        return None
        
    def evaluate_expression(self, expr: str) -> int:
        """Evaluate a constant expression, substituting known constants.
        
        This is a simple evaluation that supports:
        - Basic arithmetic: +, -, *, /, %, &, |, ^, ~, << (lshift), >> (rshift)
        - Comparisons: ==, !=, <, >, <=, >=
        - Constants: any defined constant name
        
        Returns the integer result of the evaluation.
        """
        # First replace all constant names with their values
        def replace_constants(match):
            const_name = match.group(0)
            if const_name in self.constants:
                return str(self.constants[const_name])
            else:
                raise ValueError(f"Undefined constant: {const_name}")
                
        # Replace all identifiers (that aren't part of other tokens) with their values
        pattern = r'\b[A-Za-z_][A-Za-z0-9_]*\b'
        expr = re.sub(pattern, replace_constants, expr)
        
        # Now evaluate the resulting expression
        try:
            # Replace common operators with Python equivalents
            expr = expr.replace('<<', ' << ').replace('>>', ' >> ')
            
            # Use eval with a restricted environment for security
            # This is safe because we're only evaluating a transformed expression
            # with numbers and operators
            result = eval(expr, {"__builtins__": {}})
            return int(result)
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{expr}': {str(e)}")
    
    def constant_exists(self, name: str) -> bool:
        """Check if a constant with the given name exists."""
        return name in self.constants 
    
