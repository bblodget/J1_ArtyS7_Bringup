#!/usr/bin/env python

import sys
import logging
import argparse
import lark
from lark import Lark, Transformer, Tree, Token
from pathlib import Path
from .instructionset_16kb_dualport import (
    ALU_OPS,
    STACK_EFFECTS,
    D_EFFECTS,
    R_EFFECTS,
    INST_TYPES,
    JUMP_OPS,
)
import click
from typing import List, Tuple, Dict, Optional, Union
from .asm_types import (
    InstructionType,
    InstructionMetadata,
    Modifier,
    ModifierList,
    IncludeStack,
    AssemblerState,
)
from .macro_processor import MacroProcessor
from .config import AssemblerConfig
from .address_space import AddressSpace
from .control_structures import ControlStructures
import enum
import os
import re
from dataclasses import dataclass
from .directives import Directives


class J1Assembler(Transformer):
    def __init__(self, debug: bool = False):
        super().__init__()
        self.labels: Dict[str, int] = {}  # label_name -> address
        self.current_address: int = 0
        self.base_address: int = 0  # Add this to track base address for includes
        self.debug: bool = debug
        
        # Replace direct file/source tracking with AssemblerState
        self.state = AssemblerState(
            current_file="<unknown>",
            include_paths=[],
            include_stack=[],
            source_lines=[]
        )

        # Dict to store metadata for instructions
        # Key: bytecode word address
        # Value: InstructionMetadata object
        self.instruction_metadata: Dict[int, InstructionMetadata] = {}

        # Dict to store metadata for labels
        # Key: bytecode word address
        # Value: InstructionMetadata object (of type LABEL)
        self.label_metadata: Dict[int, InstructionMetadata] = {}

        # Setup logging
        self.logger = logging.getLogger("j1asm")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        
        # Initialize address space
        self.addr_space = AddressSpace()

        # Initialize macro processor
        self.macro_processor = MacroProcessor(self.addr_space, debug=debug)

        # Load the grammar
        grammar_path = Path(__file__).parent / "j1.lark"
        if not grammar_path.exists():
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}")

        try:
            self.parser = Lark.open(grammar_path, start="start")
            self.logger.debug(f"Loaded grammar from {grammar_path}")
        except Exception as e:
            raise Exception(f"Failed to load grammar: {e}")

        # Add config instance
        self.config = AssemblerConfig(debug=debug)

        # Add this to store all instructions
        self.instructions: List[InstructionMetadata] = []
        self.macros: List[InstructionMetadata] = []

        self.main_file: str = "<unknown>"  # Track the main file

        self.current_section = '.code'

        # Initialize control structures handler
        self.control_structures = ControlStructures(self.state, self.addr_space, debug)

        # Architecture flags
        self.arch_flags = {
            "fetch_type": "quickstore",  # Default to quickstore
            "alu_ops": "extended",      # Default to extended ALU
        }
        
        # Architecture constants - automatically defined based on flags
        self.constants = {
            "ARCH_FETCH_TYPE": 0,  # 0 = quickstore, 1 = dualport
            "ARCH_ALU_OPS": 1,     # 0 = original, 1 = extended
        }
        
        # Control structure state
        self._if_count = 0
        self._begin_count = 0
        self._do_count = 0
        self._control_stack = []

        # Instantiate Directives
        self.directives = Directives(self.state, self.arch_flags, self.constants, debug=debug)
        self.directives.set_assembler(self)

    def reset(self):
        """Reset the assembler state for a new assembly run."""
        # Reset address state
        self.addr_space.reset()
        
        # Clear dictionaries
        self.labels = {}
        self.constants = {
            "ARCH_FETCH_TYPE": 0,  # 0 = quickstore, 1 = dualport
            "ARCH_ALU_OPS": 1,     # 0 = original, 1 = extended
        }
        self.arch_flags = {
            "fetch_type": "quickstore",
            "alu_ops": "extended",
        }
        self.instruction_metadata = {}
        
        # Reset control structure state
        self._if_count = 0
        self._begin_count = 0
        self._do_count = 0
        self._control_stack = []
        
        # Reset processing state flags
        self.is_assembled = False
        
        # Reset the state object
        self.state = AssemblerState()
        
        # Update directives with new state and dictionaries
        self.directives = Directives(self.state, self.arch_flags, self.constants, debug=self.debug)
        self.directives.set_assembler(self)
        
        # Reset macro processor
        self.macro_processor.reset()

    def parse(self, source: str, filename: str = "<unknown>") -> Tree:
        """Parse source code with optional filename for error reporting."""
        if self.main_file == "<unknown>":
            self.main_file = filename
        self.state.current_file = filename  # Update state instead of direct attribute
        self.macro_processor.set_current_file(filename)
        # Store source lines in state
        self.state.source_lines = [line.rstrip() for line in source.splitlines()]
        
        logging.getLogger("lark").setLevel(logging.DEBUG)
        tree = self.parser.parse(source)

        self.logger.debug(tree.pretty())

        self.logger.debug("\n=== Tokens ===")
        if self.debug:
            for token in tree.scan_values(lambda v: isinstance(v, Token)):
                self.logger.debug(f"Token: {token.type} = '{token.value}'")

        return tree

    def transform(self, tree):
        """Transform the parse tree into bytecode"""
        # Reset the current address and labels before first pass
        self.current_address = 0
        self.labels = {}
        self.instruction_metadata = {}  # Clear existing instruction metadata
        self.instructions = []          # Clear existing instructions
        self.label_metadata = {}        # Clear existing label metadata
        
        # Keep track of labels we've defined in the first pass
        self._first_pass_labels = set()
        
        # First pass: Process all statements to collect labels
        self._first_pass(tree)
        
        # Reset the current address before second pass
        self.current_address = 0
        
        # Second pass: Process all statements again to generate bytecode
        return super().transform(tree)
    
    def _first_pass(self, tree):
        """First pass to collect all labels"""
        if tree.data == 'program':
            for child in tree.children:
                if hasattr(child, 'data') and child.data == 'statement':
                    for statement_child in child.children:
                        if hasattr(statement_child, 'data') and statement_child.data == 'label':
                            label_name = str(statement_child.children[1])
                            if label_name in self.labels:
                                # This is a duplicate label - raise an error
                                token = statement_child.children[1]
                                raise ValueError(
                                    f"{self.state.current_file}:{token.line}:{token.column}: "
                                    f"Duplicate label: {label_name}"
                                )
                            self.labels[label_name] = self.current_address
                            # Track that we defined this label in first pass
                            self._first_pass_labels.add(label_name)
                            self.logger.debug(f"First pass: Found label {label_name} at address {self.current_address}")
                elif hasattr(child, 'data') and child.data == 'include_stmt':
                    # When processing includes, we need to track that we've already found labels
                    self.logger.debug(f"First pass: Processing include statement, current labels: {self.labels}")
        elif hasattr(tree, 'children'):
            for child in tree.children:
                if hasattr(child, 'data'):
                    self._first_pass(child)

    def program(
        self, statements: List[Union[InstructionMetadata, List[InstructionMetadata]]]
    ) -> None:
        """Process all statements and resolve labels."""
        # First pass: collect labels and instructions
        for stmt in statements:
            if isinstance(stmt, InstructionMetadata):
                if stmt.type == InstructionType.DIRECTIVE:
                    continue    # ORG already handled
                if stmt.type == InstructionType.LABEL:
                    if stmt.word_addr == -1:
                        raise ValueError(
                            f"{self.state.current_file}:{stmt.line}:{stmt.column}: "
                            f"Label {stmt.label_name} has no word address"
                        )
                    if stmt.label_name in self.labels:
                        # If this label was already defined in our first pass, just update it
                        if stmt.label_name in self._first_pass_labels:
                            self.logger.debug(f"Updating label {stmt.label_name} from first pass address {self.labels[stmt.label_name]} to second pass address {stmt.word_addr}")
                            self.labels[stmt.label_name] = stmt.word_addr
                            self.label_metadata[stmt.word_addr] = stmt
                            continue
                        
                        # Otherwise, it's a real duplicate
                        raise ValueError(
                            f"{self.state.current_file}:{stmt.line}:{stmt.column}: "
                            f"Duplicate label: {stmt.label_name}"
                        )
                        
                    self.labels[stmt.label_name] = stmt.word_addr
                    self.label_metadata[stmt.word_addr] = stmt
                    continue

                if stmt.type == InstructionType.MACRO_DEF:
                    self.macros.append(stmt)
                    continue

                # Other Instruction types should have a word address
                if stmt.word_addr == -1:
                    raise ValueError(
                        f"{self.state.current_file}:{stmt.line}:{stmt.column}: "
                        f"Instruction {stmt.instr_text} has no word address"
                    )
                self.instructions.append(stmt)
                self.instruction_metadata[stmt.word_addr] = stmt

            elif isinstance(stmt, list):
                # Handle lists from both macro expansions and subroutine definitions
                for inst in stmt:
                    if not isinstance(inst, InstructionMetadata):
                        raise ValueError(
                            f"{self.state.current_file}: Expected InstructionMetadata, got {type(inst)}"
                        )

                    if inst.type == InstructionType.LABEL:
                        if inst.word_addr == -1:
                            raise ValueError(
                                f"{self.state.current_file}:{inst.line}:{inst.column}: "
                                f"Label {inst.label_name} has no word address"
                            )
                        if inst.label_name in self.labels:
                            # If this label was already defined in our first pass, just update it
                            if inst.label_name in self._first_pass_labels:
                                self.logger.debug(f"Updating label {inst.label_name} from first pass address {self.labels[inst.label_name]} to second pass address {inst.word_addr}")
                                self.labels[inst.label_name] = inst.word_addr
                                self.label_metadata[inst.word_addr] = inst
                                continue
                                
                            # Otherwise, it's a real duplicate
                            raise ValueError(
                                f"{self.state.current_file}:{inst.line}:{inst.column}: "
                                f"Duplicate label: {inst.label_name}"
                            )
                            
                        self.labels[inst.label_name] = inst.word_addr
                        self.label_metadata[inst.word_addr] = inst
                        continue

                    # Handle MACRO_DEF instructions within lists
                    if inst.type == InstructionType.MACRO_DEF:
                        self.macros.append(inst)
                        continue

                    # Other Instruction types should have a word address
                    if inst.word_addr == -1:
                        raise ValueError(
                            f"{self.state.current_file}:{inst.line}:{inst.column}: "
                            f"Instruction {inst.instr_text} has no word address"
                        )

                    self.instructions.append(inst)
                    self.instruction_metadata[inst.word_addr] = inst

        # Second pass: resolve jumps in place
        for inst in self.instructions:
            if inst.type == InstructionType.JUMP:
                if not inst.label_name:
                    raise ValueError(f"Jump instruction missing label name")
                if inst.label_name not in self.labels:
                    # Only raise error if we're processing the main file
                    if self.state.current_file == self.main_file:
                        raise ValueError(
                            f"{self.state.current_file}:{inst.line}:{inst.column}: "
                            f"Undefined label: {inst.label_name}"
                        )
                    else:
                        self.logger.warning(
                            f"{self.state.current_file}:{inst.line}:{inst.column}: "
                            f"Undefined label: {inst.label_name}"
                        )
                        continue
                target = self.labels[inst.label_name]
                inst.value |= target  # Modify the instruction value in place
            
            # Handle LABEL_REF instructions (standalone tick operator)
            elif inst.type == InstructionType.LABEL_REF:
                if not inst.label_name:
                    raise ValueError(f"Label reference missing label name")
                if inst.label_name not in self.labels:
                    # Only raise error if we're processing the main file
                    if self.state.current_file == self.main_file:
                        raise ValueError(
                            f"{self.state.current_file}:{inst.line}:{inst.column}: "
                            f"Undefined label in tick reference: {inst.label_name}"
                        )
                    else:
                        self.logger.warning(
                            f"{self.state.current_file}:{inst.line}:{inst.column}: "
                            f"Undefined label in tick reference: {inst.label_name}"
                        )
                        continue
                # For label references, create a literal instruction (push address onto stack)
                target = self.labels[inst.label_name]
                # convert target from word address to byte address
                target = target << 1
                inst.value = 0x8000 | target  # Literal opcode with the label address
                self.logger.debug(f"Resolved label reference '{inst.label_name}' to address {target:04x}")

        self.is_assembled = True

    def statement(
        self, items: List[Union[InstructionMetadata, Tuple[str, str]]]
    ) -> Union[InstructionMetadata, List[InstructionMetadata]]:
        """
        Handles the 'statement' rule by processing labels and instructions.
        A statement can return:
        - A single instruction or statement (InstructionMetadata)
        - A list of statements separated by whitespace
        - A list of instructions (from subroutine definitions or label+instruction pairs)
        
        Input items can be:
        - [statement_type] -> returns single statement
        - [label, instruction] -> returns [label, instruction] as list
        - [list_of_instructions] -> returns list (from subroutine definitions)
        """
        self.logger.debug(f"\nStatement items: {items}")

        # Handle empty statement
        if not items:
            return None
        
        # If we have multiple InstructionMetadata objects, return them as a list
        if len(items) > 1 and all(isinstance(item, InstructionMetadata) for item in items):
            return items  # Return all instructions
        
        # If we have a single instruction/statement, handle directly
        if len(items) == 1 and isinstance(items[0], InstructionMetadata):
            return items[0]

        # If the item is a label definition
        if isinstance(items[0], tuple) and items[0][0] == "label":
            label_name = items[0][1]
            if label_name in self.labels:
                # Check if it's a redefinition at the same address
                if self.labels[label_name] == self.current_address:
                    return InstructionMetadata(
                        addr=self.current_address,
                        code=None,
                        source=f": {label_name}",
                        filename=self.state.current_file,
                        line=self.state.source_lines[self.state.source_lines.index(items[0][1]) - 1] if self.state.source_lines else "",
                    )
                else:
                    raise ValueError(
                        f"Label {label_name} already defined at 0x{self.labels[label_name]:04x}"
                    )
            else:
                self.labels[label_name] = self.current_address
                return InstructionMetadata(
                    addr=self.current_address,
                    code=None,
                    source=f": {label_name}",
                    filename=self.state.current_file,
                    line=self.state.source_lines[self.state.source_lines.index(items[0][1]) - 1] if self.state.source_lines else "",
                )
        # Handle other statement types
        return items[0]

    def jump_op(self, items: List[Token]) -> InstructionMetadata:
        """Handle jump operations with their labels."""
        token = items[0]  # JMP token
        op = str(token)
        
        # Get the label name from labelref
        label_ref = items[1]  # This is the result from labelref method
        label_name = str(label_ref)  # This is the label name without the tick
        
        # Always add a tick to the formatted instruction text for consistency
        instr_text = f"{op} '{label_name}"

        return InstructionMetadata.from_token(
            inst_type=InstructionType.JUMP,
            value=JUMP_OPS[op],  # Base jump opcode
            token=token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            label_name=label_name,
            instr_text=instr_text,  # Add instruction text with tick
        )

    def instruction(
        self, items: List[Union[InstructionMetadata, List[InstructionMetadata], Tuple]]
    ) -> Union[InstructionMetadata, List[InstructionMetadata]]:
        """Handles the 'instruction' rule."""
        item = items[0]

        self.logger.debug(f"Processing instruction item: {item}")

        # Handle case where we get a list of instructions (from macro expansion)
        if isinstance(item, list):
            return item  # Pass through list of instructions unchanged

        # Handle InstructionMetadata directly
        if isinstance(item, InstructionMetadata):
            # Set the word address
            item.word_addr = self.addr_space.advance()
            return item

        # For backwards compatibility or special cases (like labels)
        # TODO: Check if this is needed

        # Raise an error if we get an unexpected item type
        raise ValueError(f"Unexpected instruction format: {type(item)}")

        if isinstance(item, tuple):
            item_type, value = item
            if item_type == "label":
                return item  # Pass through labels unchanged
            if item_type == "jump":
                return item  # Pass through jump instructions
            if item_type == "macro_call":
                macro_name = value[0]
                if not self.macro_processor.is_macro(macro_name):
                    raise ValueError(
                        f"{self.state.current_file}:{token.line}:{token.column}: "
                        f"Unknown macro: {macro_name}"
                    )
                return self.macro_processor.expand_macro(macro_name, value[1])

        raise ValueError(f"Unexpected instruction format: {type(item)}")

    def modifier(self, items: List[Token]) -> Modifier:
        """Convert modifiers into their machine code representation with type."""
        token = items[0]
        mod = str(token)
        self.logger.debug(f"\nModifier: processing '{mod}'")

        if mod in STACK_EFFECTS:
            value = STACK_EFFECTS[mod]
        elif mod in D_EFFECTS:
            value = D_EFFECTS[mod]
        elif mod in R_EFFECTS:
            value = R_EFFECTS[mod]
        else:
            raise ValueError(
                f"{self.state.current_file}:{token.line}:{token.column}: "
                f"Unknown modifier: {mod}"
            )

        self.logger.debug(f"Modifier result: value={value:04x}, text={mod}")
        return Modifier(value=value, text=mod, token=token)

    def modifier_list(self, items: List[Union[Modifier, Token]]) -> ModifierList:
        """Combines all modifiers into a single ModifierList."""
        self.logger.debug(f"\nModifier list items: {items}")

        result_value = 0
        texts = []
        tokens = []

        for item in items:
            if isinstance(item, Token) and item.type == "COMMA":
                continue
            elif isinstance(item, Modifier):
                result_value |= item.value
                texts.append(item.text)
                tokens.append(item.token)
            else:
                token = item if isinstance(item, Token) else items[0]
                raise ValueError(
                    f"{self.state.current_file}:{token.line}:{token.column}: "
                    f"Expected modifier, got {item}"
                )

        return ModifierList(value=result_value, text=",".join(texts), tokens=tokens)

    def modifiers(self, items: List[Union[Token, ModifierList]]) -> ModifierList:
        """Process modifiers within square brackets."""
        self.logger.debug(f"\nModifiers: processing items: {items}")

        # Skip brackets
        modifier_items = items[1:-1]  # Skip '[' and ']'

        # We should receive a single ModifierList from modifier_list()
        if len(modifier_items) != 1 or not isinstance(modifier_items[0], ModifierList):
            raise ValueError(f"Expected single ModifierList, got {modifier_items}")

        modifier_list = modifier_items[0]
        self.logger.debug(
            f"Modifiers result: value={modifier_list.value:04x}, text=[{modifier_list.text}]"
        )

        return modifier_list

    def labelref(self, items: List[Token]) -> str:
        """Convert labelref rule into a string."""
        # items[0] is TICK, items[1] is IDENT
        return str(items[1])  # Return just the label name (without the tick)

    def label(self, items: List[Token]) -> InstructionMetadata:
        """Convert label rule into InstructionMetadata."""
        self.logger.debug(f"\nLabel items: {items}")

        # Forth-style subroutine definition: COLON IDENT
        if len(items) == 2 and items[0].type == "COLON" and items[1].type == "IDENT":
            token = items[1]  # This is the IDENT token
            label_name = str(token)
            instr_text = f":{label_name}"
        else:
            raise ValueError(f"Unexpected label format: {items}")

        # Get allocation address
        addr = self.addr_space.get_word_address()

        return InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,  # Labels don't have a value
            token=token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            label_name=label_name,
            instr_text=instr_text,  # Add instruction text
            word_addr=addr,
        )

    def raw_number(self, items: List[Token]) -> InstructionMetadata:
        """Convert raw number tokens (without # prefix) to their machine code representation."""
        token = items[0]
        if token.type == "RAW_HEX":
            # Remove the $ prefix to get the raw hex number
            value = int(str(token)[1:], 16)
            if value > 0x7FFF:
                raise ValueError(
                    f"{self.state.current_file}:{token.line}:{token.column}: "
                    f"Hex number {value} out of range (0 to $7FFF for literals)"
                )
        elif token.type == "RAW_DECIMAL":
            # Parse the decimal number directly
            value = int(str(token), 10)
            if value < 0:
                raise ValueError(
                    f"{self.state.current_file}:{token.line}:{token.column}: "
                    f"Negative numbers must be constructed manually"
                )
            if value > 0x7FFF:
                raise ValueError(
                    f"{self.state.current_file}:{token.line}:{token.column}: "
                    f"Decimal number {value} out of range (0 to 32767 for literals)"
                )
        elif token.type == "RAW_CHAR":
            # Expecting format: '<char>' i.e. exactly 3 characters
            token_str = str(token)
            if len(token_str) != 3:
                raise ValueError(f"Invalid raw character literal: {token_str}")
            value = ord(token_str[1])
        else:
            raise ValueError(f"Unknown token type: {token.type}")
            
        # Set high bit (0x8000) to make this a literal instruction that pushes value onto stack
        machine_code = value | 0x8000
        
        # Create metadata with safe source line handling
        try:
            source_line = self.state.source_lines[token.line - 1] if token.line > 0 and token.line <= len(self.state.source_lines) else ""
        except IndexError:
            source_line = ""
            
        return InstructionMetadata(
            type=InstructionType.BYTE_CODE,  # This is now a literal instruction
            value=machine_code,
            token=token,
            filename=self.state.current_file,
            line=token.line if hasattr(token, 'line') else 0,
            column=token.column if hasattr(token, 'column') else 0,
            source_line=source_line,
            instr_text=str(token),  # Use token string directly
            num_value=value,
            word_addr=self.addr_space.get_word_address(),
        )

    def basic_alu(self, items: List[Token]) -> Token:
        """Convert basic_alu rule into its token."""
        # items[0] is the Token for the ALU operation
        return items[0]

    def alu_op(self, items: List[Union[Token, ModifierList]]) -> InstructionMetadata:
        """Convert ALU operations into their machine code representation."""
        token = items[0]  # This is the basic ALU operation token
        base_op = str(token)
        modifier_value = 0

        # Get the base ALU operation code
        if base_op not in ALU_OPS:
            raise ValueError(
                f"{self.state.current_file}:{token.line}:{token.column}: "
                f"Unknown ALU operation '{base_op}'"
            )

        # Process modifiers if present
        instr_text = base_op
        if len(items) > 1 and isinstance(items[1], ModifierList):
            modifier_list = items[1]
            modifier_value = modifier_list.value
            instr_text = f"{base_op}[{modifier_list.text}]"

        # Combine all parts of the instruction
        result = ALU_OPS[base_op] | modifier_value | INST_TYPES["alu"]

        return InstructionMetadata.from_token(
            inst_type=InstructionType.BYTE_CODE,
            value=result,
            token=token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=instr_text,
        )

    def data_stack_delta(self, items):
        """Convert data stack delta rule into its token."""
        return items[0]

    def return_stack_delta(self, items):
        """Convert return stack delta rule into its token."""
        return items[0]

    def stack_delta(self, items):
        """Convert stack delta rule into its token."""
        return items[0]

    def stack_effect(self, items):
        """Convert stack effect rule into its token."""
        return items[0]

    def generate_listing_line(
        self, addr: int, code: int, metadata: InstructionMetadata
    ) -> str:
        """Generate a single line for the listing file with explicit field spacing."""
        # Define spacing constants
        addr_space = " " * 5  # After address
        mcode_space = " " * 10  # After machine code
        line_num_space = " " * 2  # After line:col
        source_space = " " * 4  # Before source code
        comment_space = " " * 2  # Before comment
        indent = " " * 2  # Indentation for code under labels

        # Calculate byte address
        byte_addr = addr * 2

        # Get comment from original source line
        comment_part = ""
        if "//" in metadata.source_line:
            _, comment_part = metadata.source_line.split("//", 1)
            comment_part = comment_part.strip()

        # Add macro annotation to comment if from macro
        if metadata.macro_name:
            macro_note = f"(macro: {metadata.macro_name})"
            if comment_part:
                comment_part = f"{macro_note} {comment_part}"
            else:
                comment_part = macro_note

        # Format line:col with fixed width
        line_col = f"{metadata.line:3d}:{metadata.column:<3d}"

        # Use instr_text for the instruction display
        code_part = metadata.instr_text
        if metadata.type != InstructionType.LABEL:
            code_part = f"{indent}{code_part}"

        # Format the line with explicit spacing
        if metadata.type == InstructionType.DIRECTIVE:
            return (
                f"{byte_addr:04x}{addr_space}"
                f"{addr:04x}{addr_space}"
                f"{code:04x}{mcode_space}"
                f"{line_col}{line_num_space}"
                f"{code_part:<32}"
                f"{comment_space}//{comment_space}{comment_part if comment_part else ''}\n"
            )
        elif metadata.type == InstructionType.LABEL:
            return (
                f"{byte_addr:04x}{addr_space}"
                f"{addr:04x}{addr_space}"
                f"----{mcode_space}"
                f"{line_col}{line_num_space}"
                f"{code_part:<30}{indent}"
                f"{comment_space}//{comment_space}{comment_part if comment_part else ''}\n"
            )
        else:
            return (
                f"{byte_addr:04x}{addr_space}"
                f"{addr:04x}{addr_space}"
                f"{code:04x}{mcode_space}"
                f"{line_col}{line_num_space}"
                f"{code_part:<32}"
                f"{comment_space}//{comment_space}{comment_part if comment_part else ''}\n"
            )

    def generate_listing(self, filename: str) -> None:
        """Generate listing file with both byte and word addresses."""
        with open(filename, 'w') as f:
            # Write header with column labels aligned with data columns
            f.write("BYTE     WORD     CODE            #:col    SOURCE\n")
            f.write("-" * 70 + "\n")  # Extended line to match wider format

            # Process instructions in order
            for word_addr in sorted(self.instruction_metadata.keys()):
                # First check if there's a label at this address
                if word_addr in self.label_metadata:
                    label_metadata = self.label_metadata[word_addr]
                    f.write(self.generate_listing_line(word_addr, 0, label_metadata))

                # Now process the instruction
                metadata = self.instruction_metadata[word_addr]
                f.write(self.generate_listing_line(word_addr, metadata.value, metadata))

    def generate_symbols(self, output_file: str):
        """Generate symbol file showing addresses and their associated labels."""
        if not self.is_assembled:
            raise ValueError("Cannot generate symbols before assembling")

        with open(output_file, "w") as f:
            # Sort symbols by address for readability
            sorted_symbols = sorted(self.labels.items(), key=lambda x: x[1])
            for symbol, addr in sorted_symbols:
                print(f"{addr:04x} {symbol}", file=f)

    def get_bytecodes(self) -> List[int]:
        """Return a list of resolved bytecodes for testing."""
        if not self.is_assembled:
            raise ValueError("Cannot get bytecodes before assembling")

        bytecodes = []
        prev_word_addr = 0

        # Process instructions in order by address
        for word_addr in sorted(self.instruction_metadata.keys()):
            inst = self.instruction_metadata[word_addr]
            
            # Fill gaps with zeros
            while prev_word_addr < word_addr:
                bytecodes.append(0x0000)
                prev_word_addr += 1

            if inst.type == InstructionType.BYTE_CODE or inst.type == InstructionType.JUMP or inst.type == InstructionType.NUMBER or inst.type == InstructionType.LABEL_REF:
                bytecodes.append(inst.value)
                prev_word_addr = word_addr + 1

        return bytecodes

    def generate_output(self, output_file: str):
        """Generate output file containing machine code in hex format."""
        if not self.is_assembled:
            raise ValueError("Cannot generate output before assembling")

        bytecodes = self.get_bytecodes()
        
        with open(output_file, "w") as f:
            for code in bytecodes:
                print(f"{code:04x}", file=f)

    def macro_def(self, items):
        """Handle macro definitions by delegating to macro processor."""
        self.logger.debug(f"Processing macro definition: {items}")
        macro_token = items[0]  # MACRO token
        name_token = items[1]  # IDENT token
        macro_name = str(name_token)

        # Process the macro definition
        self.macro_processor.process_macro_def(items)

        # Create instruction text for the macro definition
        # Include stack effect comment if present
        stack_effect = ""
        for item in items:
            if isinstance(item, Token) and item.type == "STACK_COMMENT":
                stack_effect = f" {str(item)}"
                break

        instr_text = f"macro: {macro_name}{stack_effect}"

        # Return InstructionMetadata instead of tuple
        return InstructionMetadata.from_token(
            inst_type=InstructionType.MACRO_DEF,
            value=0,  # No machine code value needed for macro definition
            token=name_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=instr_text,  # Add formatted instruction text
            macro_name=macro_name,
        )

    def call_expr(self, items: List[Token]) -> List[InstructionMetadata]:
        """Handle word calls, checking for loop index words (i, j, k)."""
        token = items[0]
        word = token.value

        # Special handling for loop index words
        if word in ["i", "j", "k"]:
            # Get loop depth from control structures
            depth = self.control_structures.get_do_loop_depth()
            
            if not self.control_structures.is_in_do_loop():
                self.logger.warning(
                    f"{self.state.current_file}:{token.line}:{token.column}: "
                    f"'{word}' used outside DO LOOP"
                )
            elif word == "j" and depth < 2:
                self.logger.warning(
                    f"{self.state.current_file}:{token.line}:{token.column}: "
                    f"'j' used in non-nested DO LOOP"
                )
            elif word == "k" and depth < 3:
                self.logger.warning(
                    f"{self.state.current_file}:{token.line}:{token.column}: "
                    f"'k' used in insufficiently nested DO LOOP (depth: {depth})"
                )

            # Generate appropriate instruction based on nesting level
            if word == "i":
                return self.control_structures._generate_rstack_access(0, token)
            elif word == "j":
                return self.control_structures._generate_rstack_access(1, token)
            else:  # k
                return self.control_structures._generate_rstack_access(2, token)

        # Check if the identifier is a defined macro
        if self.macro_processor.is_macro(word):
            # Expand as a macro
            return self.macro_processor.expand_macro(word, token)
        else:
            # Otherwise, treat it as a subroutine call.
            # Create an InstructionMetadata for a CALL instruction by populating:
            # - inst_type as JUMP (to be resolved as a CALL during label resolution)
            # - value with the CALL opcode
            # - label_name set to the identifier (subroutine name)
            instr_text = f"CALL {word}"
            return InstructionMetadata.from_token(
                inst_type=InstructionType.JUMP,
                value=JUMP_OPS["CALL"],   # Corresponds to the subroutine call op-code
                token=token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                label_name=word,          # This is the subroutine label referenced by the CALL
                instr_text=instr_text,
                word_addr=self.addr_space.get_word_address(),
            )

    def include_stmt(self, items: List[Token]) -> List[InstructionMetadata]:
        """Process an include statement and return an empty list."""
        token = items[1]
        filename = str(token)[1:-1]  # Remove quotes

        try:
            # Use config to resolve include file
            resolved_path = self.config.resolve_include(
                filename, Path(self.state.current_file).parent
            )

            if resolved_path is None:
                raise FileNotFoundError(f"Include file not found: {filename}")

            # Save current state
            include_stack_entry = IncludeStack(
                filename=self.state.current_file,
                line_number=token.line,
                source_lines=self.state.source_lines,
            )

            # Read the included file using the resolved path
            with open(
                resolved_path, "r"
            ) as f:  # Changed from filename to resolved_path
                included_source = f.read()
                included_lines = [
                    line.rstrip() for line in included_source.splitlines()
                ]

            # Parse and process the included file
            self.logger.debug(
                f"Processing include file: {resolved_path}"
            )  # Updated log message

            # Save current state to stack
            self.state.include_stack.append(include_stack_entry)

            # Set new current state
            self.state.current_file = str(resolved_path)  # Use resolved path as current file
            self.state.source_lines = included_lines

            # Parse and process the included file
            tree = self.parser.parse(included_source)
            self.transform(tree)

            # Restore previous state
            prev_state = self.state.include_stack.pop()
            self.state.current_file = prev_state.filename
            self.state.source_lines = prev_state.source_lines

            # Return empty list since include itself doesn't generate instructions
            return []

        except Exception as e:
            raise ValueError(
                f"{self.state.current_file}:{token.line}:{token.column}: "
                f"Error processing include file {filename}: {str(e)}"
            )

    def format_include_trace(self) -> str:
        """Format the include stack for error messages."""
        if not self.state.include_stack:
            return ""

        trace = []
        for entry in reversed(self.state.include_stack):
            trace.append(f"Included from {entry.filename}:{entry.line_number}")
        return "\n".join(trace)

    def org_directive(self, items):
        """Handle ORG directive with word address"""
        number = items[1]  # This should be raw_number now
        
        address = number.num_value & 0xFFFF  # Ensure 16-bit
        self.addr_space.set_org(address)
        
        # Create metadata with safe source line handling
        try:
            source_line = self.state.source_lines[number.token.line - 1] if number.token.line > 0 and number.token.line <= len(self.state.source_lines) else ""
        except IndexError:
            source_line = ""
            
        # Create metadata for listing
        return InstructionMetadata(
            type=InstructionType.DIRECTIVE,
            value=address,
            token=number.token,
            filename=self.state.current_file,
            line=number.token.line if hasattr(number.token, 'line') else 0,
            column=number.token.column if hasattr(number.token, 'column') else 0,
            source_line=source_line,
            instr_text=f"ORG {number.instr_text}",
        )

    def _generate_unique_label(self, base: str) -> str:
        """Generate a unique temporary label for control structures."""
        if not hasattr(self, '_label_counter'):
            self._label_counter = 0
        label_name = f"{base}_{self._label_counter}"
        self._label_counter += 1
        return label_name

    def if_then(self, items):
        """
        Transform an IF THEN control structure.
        
        Grammar rule:
            if_then: IF block THEN
            
        Because the block instructions have already been assigned addresses,
        we first determine the starting address of the block. Then, we insert a 
        conditional jump at that address and adjust the addresses of all block
        instructions by incrementing them by one.
        
        This method generates:
        1. A conditional jump (ZJMP) inserted before the block.
        2. The adjusted block instructions.
        3. A label marking the end of the IF block.
        """
        # items[0] is the IF token, items[1] is the block tree, items[2] is the THEN token.
        if_token = items[0]
        block_tree = items[1]
        then_token = items[2]

        # Generate a unique label for the false branch.
        false_label = self._generate_unique_label("if_false")

        # Process the block instructions (they already have addresses).
        if not isinstance(block_tree, Tree):
            raise ValueError("Block tree is not a valid tree")
        
        block_instructions = [] 
        for instruction in block_tree.children:
            if isinstance(instruction, list):
                block_instructions.extend(instruction)
            elif isinstance(instruction, InstructionMetadata):
                block_instructions.append(instruction)
            else:
                raise ValueError("Block instruction is not a valid instruction")

        # Determine the start address of the block.
        # If there are instructions, use the first one's address;
        # otherwise, use the current address from the address space.
        if block_instructions:
            first_instr = block_instructions[0]
            block_start_addr = first_instr.word_addr
        else:
            block_start_addr = self.addr_space.get_word_address()

        # Create the conditional jump instruction at the block's start address.
        cond_jump = InstructionMetadata.from_token(
            inst_type=InstructionType.JUMP,
            value=JUMP_OPS["ZJMP"],
            token=if_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            label_name=false_label,
            instr_text=f"ZJMP {false_label}: IF",
            word_addr=block_start_addr,
        )

        # We inserted the jump instruction before the block;
        # update the addresses of all block instructions by +1.
        for instr in block_instructions:
            instr.word_addr += 1

        # Advance the address space since we added the JUMP instruction
        self.addr_space.advance()

        # End label points at word after last word in block
        end_label_addr = instr.word_addr + 1

        then_label_instr = InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,  # Labels do not carry machine code value.
            token=then_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=f"{false_label}: THEN",
            label_name=false_label,
            word_addr=end_label_addr,
        )


        # Return the complete sequence:
        # 1. The conditional jump,
        # 2. The adjusted block instructions,
        # 3. And finally the THEN label.
        return [cond_jump] + block_instructions + [then_label_instr]

    def if_else_then(self, items):
        """
        Transform an IF ELSE THEN control structure.
        
        Grammar rule:
            if_else_then: IF block ELSE block THEN
            
        This transformation converts:
            IF
                true_block
            ELSE
                false_block
            THEN
            next_instr

        Into:
            +ZJMP if_false_label   ; Jump to false block if condition is false
            true_block             ; Execute if condition was true
            +JMP if_end_label      ; Skip over false block
            +if_false_label:       ; Target for condition == false
            false_block            ; Execute if condition was false
            +if_end_label:         ; Continue with next instruction
            next_instr

        The + indicates instructions/labels we insert. Because the block 
        instructions already have addresses assigned, we:
        1. Insert ZJMP before true_block (adjust true_block addresses by +1)
        2. Insert JMP after true_block
        3. Insert if_false_label before false_block (adjust false_block addresses by +1)
        4. Insert if_end_label after false_block
        """
        # Unpack tokens and block trees from the items.
        # items[0] is the IF token.
        # items[1] is the true block tree.
        # items[2] is the ELSE token.
        # items[3] is the false block tree.
        # items[4] is the THEN token.
        if_token = items[0]
        true_block_tree = items[1]
        else_token = items[2]
        false_block_tree = items[3]
        then_token = items[4]

        # Generate unique labels for the false branch and the end of the IF ELSE structure.
        false_label = self._generate_unique_label("if_false")
        end_label = self._generate_unique_label("if_end")

        ##############################################################################
        # Process the TRUE block.
        ##############################################################################
        # Process the block instructions (they already have addresses).
        if not isinstance(true_block_tree, Tree):
            raise ValueError("TRUE block tree is not a valid tree")

        true_instructions = [] 
        for instruction in true_block_tree.children:
            if isinstance(instruction, list):
                true_instructions.extend(instruction)
            elif isinstance(instruction, InstructionMetadata):
                true_instructions.append(instruction)
            else:
                raise ValueError("Block instruction is not a valid instruction")

        # Increment the addresses of all true block instructions by +1.
        # So we can insert the conditional jump at the start of the true block.
        for instr in true_instructions:
            instr.word_addr += 1

        ##############################################################################
        # Process the FALSE block.
        ##############################################################################
        # Process the block instructions (they already have addresses).
        if not isinstance(false_block_tree, Tree):
            raise ValueError("FALSE block tree is not a valid tree")
        
        false_instructions = [] 
        for instruction in false_block_tree.children:
            if isinstance(instruction, list):
                false_instructions.extend(instruction)
            elif isinstance(instruction, InstructionMetadata):
                false_instructions.append(instruction)
            else:
                raise ValueError("Block instruction is not a valid instruction")

        # Increment the address of all the false block instructions by +2.
        # So we can insert the conditional jump at the start of the true block.
        # And the JMP if_end_label after the true block.
        for instr in false_instructions:
            instr.word_addr += 2

        ##############################################################################
        # Insert ZJMP if_false before the true block.
        ##############################################################################

        # Determine the starting address of the true block.
        if true_instructions:
            true_start_addr = true_instructions[0].word_addr
        else:
            raise ValueError("True block is empty")

        # Create a conditional jump (ZJMP) at the true block's start address.
        cond_jump = InstructionMetadata.from_token(
            inst_type=InstructionType.JUMP,
            value=JUMP_OPS["ZJMP"],
            token=if_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            label_name=false_label,
            instr_text=f"ZJMP {false_label}: IF",
            word_addr=(true_start_addr-1),
        )

        ##############################################################################
        # Insert JMP if_end after the true block to skip the false block.
        ##############################################################################

        # Determine the ending address of the true block.
        true_end_addr = true_instructions[-1].word_addr

        # Create an unconditional jump (JMP) at the end of the true block.
        # This will skip the false block if the condition is true.
        uncond_jump = InstructionMetadata.from_token(
            inst_type=InstructionType.JUMP,
            value=JUMP_OPS["JMP"],
            token=else_token,  # Using the ELSE token; you could also create a synthetic token.
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            label_name=end_label,
            instr_text=f"JMP {end_label}: ELSE",
            word_addr=(true_end_addr+1),
        )

        ##############################################################################
        # Insert the false block label at the false block's start address.
        ##############################################################################

        # Determine the starting address of the false block.
        if false_instructions:
            false_start_addr = false_instructions[0].word_addr
        else:
            raise ValueError("False block is empty")

        # Insert the false block label at the false block's start address.
        false_label_instr = InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,  # Labels carry no machine-code value.
            token=else_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=f"{false_label}: ELSE",
            label_name=false_label,
            word_addr=false_start_addr,
        )

        ##############################################################################
        # Insert the end if label after the false block.
        ##############################################################################

        # Determine the ending address of the false block.
        false_end_addr = false_instructions[-1].word_addr

        # Insert the end if label at the end of the false block.
        end_label_instr = InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,
            token=then_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=f"{end_label}: THEN",
            label_name=end_label,
            word_addr=(false_end_addr+1),
        )

        ##############################################################################
        # Advance the address space to account for the two new jump instructions.
        ##############################################################################
        self.addr_space.advance()
        self.addr_space.advance()


        ##############################################################################
        # Return the complete sequence:
        # 1. The conditional jump (ZJMP) for the IF.
        # 2. The adjusted true block instructions.
        # 3. The unconditional jump (JMP) to skip the false block.
        # 4. The false block label instruction.
        # 5. The adjusted false block instructions.
        # 6. The THEN label instruction.
        ##############################################################################
        return [cond_jump] + true_instructions + [uncond_jump, false_label_instr] + false_instructions + [end_label_instr]

    def loop_until(self, items):
        """
        Transform a BEGIN ... UNTIL loop structure.
        
        Grammar rule:
            loop_until: BEGIN block UNTIL
            
        This transforms:
            BEGIN
                block           ; Block leaves test condition on stack
            UNTIL
            next_instr
            
        Into:
            +begin_label:
            block              ; Block code, leaves condition on stack
            ZJMP begin_label   ; Jump back to begin if condition is false
            next_instr
        """
        begin_token = items[0]  # BEGIN token
        block_tree = items[1]   # block tree
        until_token = items[2]  # UNTIL token
        
        # Generate unique label for loop start
        begin_label = self._generate_unique_label("begin")
        
        # Process block instructions
        if not isinstance(block_tree, Tree):
            raise ValueError("Block tree is not a valid tree")
        
        block_instructions = []
        for instruction in block_tree.children:
            if isinstance(instruction, list):
                block_instructions.extend(instruction)
            elif isinstance(instruction, InstructionMetadata):
                block_instructions.append(instruction)
            else:
                raise ValueError("Block instruction is not a valid instruction")
                
        # Create begin label at start of block
        begin_label_instr = InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,
            token=begin_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=f"{begin_label}: BEGIN",
            label_name=begin_label,
            word_addr=block_instructions[0].word_addr
        )
        
        # Create conditional jump back to begin
        jump_instr = InstructionMetadata.from_token(
            inst_type=InstructionType.JUMP,
            value=JUMP_OPS["ZJMP"],
            token=until_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            label_name=begin_label,
            instr_text=f"ZJMP {begin_label}: UNTIL",
            word_addr=block_instructions[-1].word_addr + 1
        )
        
        # Advance address space for the jump instruction
        self.addr_space.advance()
        
        # Return complete sequence
        return [begin_label_instr] + block_instructions + [jump_instr]

    def loop_while(self, items):
        """
        Transform a BEGIN ... WHILE ... REPEAT loop structure.
        
        Grammar rule:
            loop_while: BEGIN block WHILE block REPEAT
            
        This transforms:
            BEGIN
                block1          ; First block executes unconditionally
            WHILE              ; Block1 leaves test condition on stack
                block2          ; Second block executes if condition is true
            REPEAT             ; Jump back to BEGIN
            next_instr
            
        Into:
            +begin_label:
            block1             ; First block code
            ZJMP exit_label    ; If condition is false, exit loop
            block2             ; Second block code
            JMP begin_label    ; Jump back to start unconditionally
            +exit_label:       ; Target for condition == false
            next_instr
        """
        begin_token = items[0]    # BEGIN token
        block1_tree = items[1]    # First block tree
        while_token = items[2]    # WHILE token
        block2_tree = items[3]    # Second block tree
        repeat_token = items[4]   # REPEAT token
        
        # Generate unique labels for loop start and exit
        begin_label = self._generate_unique_label("begin")
        exit_label = self._generate_unique_label("exit")
        
        ##############################################################################
        # Process block1 instructions
        ##############################################################################
        if not isinstance(block1_tree, Tree):
            raise ValueError("Block1 tree is not a valid tree")
        
        block1_instructions = []
        for instruction in block1_tree.children:
            if isinstance(instruction, list):
                block1_instructions.extend(instruction)
            elif isinstance(instruction, InstructionMetadata):
                block1_instructions.append(instruction)
            else:
                raise ValueError("Block instruction is not a valid instruction")
            
        ##############################################################################
        # Process block2 instructions
        ##############################################################################
        if not isinstance(block2_tree, Tree):
            raise ValueError("Block2 tree is not a valid tree")
        
        block2_instructions = []
        for instruction in block2_tree.children:
            if isinstance(instruction, list):
                block2_instructions.extend(instruction)
            elif isinstance(instruction, InstructionMetadata):
                block2_instructions.append(instruction)
            else:
                raise ValueError("Block instruction is not a valid instruction")
        
        # Increment addresses of block2 instructions by 1 to make room for the ZJMP
        for instr in block2_instructions:
            instr.word_addr += 1
        
        ##############################################################################
        # Create begin label at start of block1
        ##############################################################################
        begin_label_instr = InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,
            token=begin_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=f"{begin_label}: BEGIN",
            label_name=begin_label,
            word_addr=block1_instructions[0].word_addr
        )
        
        ##############################################################################
        # Create conditional jump to exit after WHILE condition
        ##############################################################################
        cond_jump = InstructionMetadata.from_token(
            inst_type=InstructionType.JUMP,
            value=JUMP_OPS["ZJMP"],
            token=while_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            label_name=exit_label,
            instr_text=f"ZJMP {exit_label}: WHILE",
            word_addr=block1_instructions[-1].word_addr + 1
        )
        
        ##############################################################################
        # Create unconditional jump back to begin at end of block2
        ##############################################################################
        repeat_jump = InstructionMetadata.from_token(
            inst_type=InstructionType.JUMP,
            value=JUMP_OPS["JMP"],
            token=repeat_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            label_name=begin_label,
            instr_text=f"JMP {begin_label}: REPEAT",
            word_addr=block2_instructions[-1].word_addr + 1
        )
        
        ##############################################################################
        # Create exit label after the loop
        ##############################################################################
        exit_label_instr = InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,
            token=repeat_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=f"{exit_label}: END-WHILE",
            label_name=exit_label,
            word_addr=repeat_jump.word_addr + 1
        )
        
        # Advance address space for both jump instructions
        self.addr_space.advance()  # For ZJMP
        self.addr_space.advance()  # For JMP
        
        # Return complete sequence:
        # 1. Begin label
        # 2. Block1 instructions
        # 3. Conditional jump to exit
        # 4. Block2 instructions
        # 5. Unconditional jump back to begin
        # 6. Exit label
        return [begin_label_instr] + block1_instructions + [cond_jump] + \
               block2_instructions + [repeat_jump, exit_label_instr]

    def do_loop(self, items):
        """Delegate DO LOOP processing to control structures handler."""
        return self.control_structures.do_loop(items)

    def do_op(self, items):
        """Delegate DO token processing to control structures handler."""
        return self.control_structures.do_op(items)

    def loop_op(self, items):
        """Delegate LOOP token processing to control structures handler."""
        return self.control_structures.loop_op(items)

    def plus_loop_op(self, items):
        """Delegate +LOOP token processing to control structures handler."""
        return self.control_structures.plus_loop_op(items)

    def do_plus_loop(self, items):
        """
        Transform a DO +LOOP control structure.
        
        Grammar rule:
            do_plus_loop: DO block PLUS_LOOP
            
        This transforms:
        10 0 DO     ; limit=10, index=0
           block    ; Loop body
           2        ; increment by 2
        +LOOP

        Into:
        >r          ; Save index (0) to R stack
        >r          ; Save limit (10) to R stack
        +do_label:  ; Start of loop
        block       ; Execute loop body
        r>          ; Get limit
        r>          ; Get index
        +           ; Add increment to index
        dup         ; Duplicate increment for checking
        0 <         ; Check if increment is negative
        ZJMP skip_swap_label  ; Skip swap if increment >= 0
        swap        ; Swap operands if increment negative
        skip_swap_label:      ; Label for skipping swap
        2dup<       ; Compare (swapped if negative)
        >r          ; Save new index back
        >r          ; Save limit back
        ZJMP do_label  ; Jump if comparison true
        drop        ; Clean up extra copy of index
        drop        ; Clean up extra copy of limit
        """
        do_token = items[0]  # DO token
        block_tree = items[1]  # block tree
        plus_loop_token = items[2]  # +LOOP token
        
        # Generate unique labels for loop start and skip_swap
        do_label = self._generate_unique_label("do")
        skip_swap_label = self._generate_unique_label("skip_swap")
        
        # Process block instructions
        if not isinstance(block_tree, Tree):
            raise ValueError("Block tree is not a valid tree")
        
        block_instructions = []
        for instruction in block_tree.children:
            if isinstance(instruction, list):
                block_instructions.extend(instruction)
            elif isinstance(instruction, InstructionMetadata):
                block_instructions.append(instruction)
            else:
                raise ValueError("Block instruction is not a valid instruction")
        
        # Increment addresses of block instructions by 2 to make room for the >r >r setup
        for instr in block_instructions:
            instr.word_addr += 2
        
        # Create setup instructions (>r >r)
        setup_instrs = [
            # >r for index
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["T"] | STACK_EFFECTS["T->R"],  # T->R effect
                token=do_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="T[T->R]  \\ Save index to R stack",
                word_addr=block_instructions[0].word_addr - 2
            ),
            # >r for limit
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["T"] | STACK_EFFECTS["T->R"],  # T->R effect
                token=do_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="T[T->R]  \\ Save limit to R stack",
                word_addr=block_instructions[0].word_addr - 1
            )
        ]
        
        # Create loop start label
        do_label_instr = InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL,
            value=0,
            token=do_token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=f"{do_label}: DO",
            label_name=do_label,
            word_addr=block_instructions[0].word_addr
        )
        
        # Create loop end instructions
        loop_end_instrs = [
            # r> get limit
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["rT"],  # rT operation
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="rT  \\ Get limit",
                word_addr=block_instructions[-1].word_addr + 1
            ),
            # r> get index
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["rT"],  # rT operation
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="rT  \\ Get index",
                word_addr=block_instructions[-1].word_addr + 2
            ),
            # + add increment to index
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["T+N"],  # T+N operation
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="T+N  \\ Add increment to index",
                word_addr=block_instructions[-1].word_addr + 3
            ),
            # dup to check if increment is negative
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["T"] | STACK_EFFECTS["T->N"] | D_EFFECTS["d+1"],
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="T[T->N,d+1]  \\ Duplicate increment",
                word_addr=block_instructions[-1].word_addr + 4
            ),
            # Check if increment is negative (compare with 0)
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["N<T"],  # N<T operation
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="N<T  \\ Check if increment < 0",
                word_addr=block_instructions[-1].word_addr + 5
            ),
            # ZJMP to skip_swap if increment >= 0
            InstructionMetadata.from_token(
                inst_type=InstructionType.JUMP,
                value=JUMP_OPS["ZJMP"],
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                label_name=skip_swap_label,
                instr_text=f"ZJMP {skip_swap_label}  \\ Skip swap if increment >= 0",
                word_addr=block_instructions[-1].word_addr + 6
            ),
            # swap if increment is negative
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["N"] | STACK_EFFECTS["T->N"],
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="N[T->N]  \\ Swap if increment negative",
                word_addr=block_instructions[-1].word_addr + 7
            ),
            # skip_swap label and 2dup< share the same address
            InstructionMetadata.from_token(
                inst_type=InstructionType.LABEL,
                value=0,
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                label_name=skip_swap_label,
                instr_text=f"{skip_swap_label}:",
                word_addr=block_instructions[-1].word_addr + 8
            ),
            # 2dup< at same address as label
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["N<T"] | STACK_EFFECTS["T->N"] | D_EFFECTS["d+1"],
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="N<T[T->N,d+1]  \\ 2dup<",
                word_addr=block_instructions[-1].word_addr + 8  # Same address as skip_swap label
            ),
            # >r save new index
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["T"] | STACK_EFFECTS["T->R"],  # T->R effect
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="T[T->R]  \\ Save new index back",
                word_addr=block_instructions[-1].word_addr + 9
            ),
            # >r save limit
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["T"] | STACK_EFFECTS["T->R"],  # T->R effect
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="T[T->R]  \\ Save limit back",
                word_addr=block_instructions[-1].word_addr + 10
            ),
            # ZJMP do_label
            InstructionMetadata.from_token(
                inst_type=InstructionType.JUMP,
                value=JUMP_OPS["ZJMP"],
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                label_name=do_label,
                instr_text=f"ZJMP {do_label}  \\ Jump if comparison true",
                word_addr=block_instructions[-1].word_addr + 11
            ),
            # drop (first)
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["N"],  # N operation = drop
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="N  \\ Clean up index",
                word_addr=block_instructions[-1].word_addr + 12
            ),
            # drop (second)
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=ALU_OPS["N"],  # N operation = drop
                token=plus_loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="N  \\ Clean up limit",
                word_addr=block_instructions[-1].word_addr + 13
            )
        ]
        
        # Advance address space for all the instructions we added
        for _ in range(2 + len(loop_end_instrs)):  # 2 setup + loop end instructions
            self.addr_space.advance()
        
        # Return complete sequence:
        # 1. Setup instructions (>r >r)
        # 2. Loop start label
        # 3. Block instructions
        # 4. Loop end instructions
        return setup_instrs + [do_label_instr] + block_instructions + loop_end_instrs

    def memory_init_statement(self, items):
        """Process memory initialization statements."""
        # items[0] should be a raw number token (hex or decimal)
        # items[1] should be COMMA token
        token = items[0]
        instr_text = f"{token},"
        
        # Handle raw hex literal
        if token.type == "RAW_HEX":
            value = int(str(token)[1:], 16)
        elif token.type == "RAW_DECIMAL":
            value = int(str(token), 10)
        elif token.type == "RAW_CHAR":
            token_str = str(token)
            if len(token_str) != 3:
                raise ValueError(f"Invalid raw character literal in memory initialization: {token_str}")
            value = ord(token_str[1])
        else:
            raise ValueError(f"Unexpected token type: {token.type}")
        
        # Create metadata and assign address
        addr = self.addr_space.advance()
        metadata = InstructionMetadata(
            type=InstructionType.NUMBER,
            value=value,
            token=token,
            filename=self.state.current_file,
            line=token.line,
            column=token.column,
            source_line=self.state.source_lines[token.line - 1],
            instr_text=instr_text,
            word_addr=addr,
            num_value=value,
        )
        
        # Add to tracked instructions
        self.instruction_metadata[addr] = metadata
        self.instructions.append(metadata)
        
        # Return the metadata
        return metadata
        
    def address_of(self, items):
        """Handle standalone tick operations that push label addresses onto the stack."""
        # items[0] is TICK, items[1] is IDENT
        token = items[1]  # This is the IDENT token
        label_name = str(token)  # Label name (without the tick)
        
        # Format for instruction text representation
        instr_text = f"'{label_name}"
        
        # Create a placeholder instruction - the real address/value will be filled in during second pass
        # when all labels are known
        metadata = InstructionMetadata.from_token(
            inst_type=InstructionType.LABEL_REF,
            value=0,  # Placeholder, will be filled with 0x8000 | address in second pass
            token=token,
            filename=self.state.current_file,
            source_lines=self.state.source_lines,
            instr_text=instr_text,
            label_name=label_name,
        )
        
        # NOTE: We do NOT advance the address space here as the instruction method will do that
        # Do NOT add to tracked instructions here either - instruction method will handle that
        
        return metadata
    
    def arch_flag_directive(self, items):
        """Handle architecture flag directives, delegating to the directives class"""
        return self.directives.arch_flag_directive(items)

    def define_directive(self, items):
        """Handle constant definition directives, delegating to the directives class"""
        return self.directives.define_directive(items)


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option(
    "-o", "--output", type=click.Path(), help="Output file (default: aout.hex)"
)
@click.option("-d", "--debug", is_flag=True, help="Enable debug output")
@click.option("--symbols", is_flag=True, help="Generate symbol file (.sym)")
@click.option("--listing", is_flag=True, help="Generate listing file (.lst)")
@click.option(
    "-I",
    "--include",
    multiple=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Add directory to include search path",
)
@click.option("--no-stdlib", is_flag=True, help="Disable standard library include path")
def main(input, output, debug, symbols, listing, include, no_stdlib):
    """J1 Forth CPU Assembler"""
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(levelname)s: %(message)s",
            stream=sys.stderr,
        )
        logger = logging.getLogger("j1asm")

        # Set default output file if not specified
        output = output or "aout.hex"

        # Read the input file
        with open(input, "r") as f:
            source = f.read()
            logger.debug(f"Source code:\n{source}")

        logger.debug("Parsing source...")

        assembler = J1Assembler(debug=debug)

        # Configure include paths
        for path in include:
            assembler.config.add_include_path(path)

        if no_stdlib:
            assembler.config.disable_stdlib()

        try:
            tree = assembler.parse(source, filename=input)
            assembler.transform(tree)

            # Write output to specified file
            assembler.generate_output(output)
            logger.info(f"Successfully wrote output to {output}")

            # Generate symbol file if requested
            if symbols:
                sym_file = Path(output).with_suffix(".sym")
                assembler.generate_symbols(sym_file)
                logger.info(f"Generated symbol file: {sym_file}")

            # Generate listing file if requested
            if listing:
                lst_file = Path(output).with_suffix(".lst")
                assembler.generate_listing(lst_file)
                logger.info(f"Generated listing file: {lst_file}")

        except lark.exceptions.UnexpectedInput as e:
            # Format Lark's parsing errors to match our style
            error_msg = str(e)
            if ", at line" in error_msg:
                error_msg = error_msg.split(", at line")[0]

            # Find the actual line with the error
            real_line = 0
            source_lines = source.splitlines()
            for i, line in enumerate(source_lines[: e.line - 1], 1):
                stripped = line.strip()
                if stripped and not stripped.startswith(";"):
                    real_line = i

            error_line = source_lines[real_line - 1]
            context = f"\n    {error_line}\n    {' ' * (e.column-1)}^"

            logger.error(f"{input}:{real_line}:{e.column}: {error_msg}")
            if debug:
                logger.debug(context)
            raise click.Abort()

    except Exception as e:
        logger.error(str(e))
        if debug:
            import traceback

            logger.debug(traceback.format_exc())
        raise click.Abort()






if __name__ == "__main__":
    main()
