"""
Control structure handling for J1 assembler.
Handles IF/THEN, IF/ELSE/THEN, BEGIN/UNTIL, BEGIN/WHILE/REPEAT, and DO/LOOP structures.
"""

from typing import List, Union
from lark import Token, Tree
from .asm_types import InstructionMetadata, InstructionType, AssemblerState
from .address_space import AddressSpace
from .instructionset_16kb_dualport import (
    ALU_OPS,
    STACK_EFFECTS,
    D_EFFECTS,
    R_EFFECTS,
    INST_TYPES,
    JUMP_OPS,
)
import logging

class ControlStructures:
    def __init__(self, state: AssemblerState, addr_space: AddressSpace, debug: bool = False):
        self.state = state
        self.addr_space = addr_space
        self.debug = debug
        self.logger = logging.getLogger("j1asm.control")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        
        # Initialize DO LOOP tracking
        self._do_loop_depth = 0
        self._in_do_loop = False
        self._label_counter = 0

    def _generate_unique_label(self, base: str) -> str:
        """Generate a unique temporary label for control structures."""
        label_name = f"{base}_{self._label_counter}"
        self._label_counter += 1
        return label_name

    def do_op(self, items: List[Token]) -> Token:
        """Handle DO token."""
        self._in_do_loop = True
        self._do_loop_depth += 1
        return items[0]  # Return the DO token

    def loop_op(self, items: List[Token]) -> Token:
        """Handle LOOP token."""
        if not self._in_do_loop:
            raise ValueError(
                f"{self.state.current_file}:{items[0].line}:{items[0].column}: "
                f"LOOP without matching DO"
            )
        self._do_loop_depth -= 1
        if self._do_loop_depth == 0:
            self._in_do_loop = False
        return items[0]  # Return the LOOP token

    def plus_loop_op(self, items: List[Token]) -> Token:
        """Handle +LOOP token."""
        if not self._in_do_loop:
            raise ValueError(
                f"{self.state.current_file}:{items[0].line}:{items[0].column}: "
                f"+LOOP without matching DO"
            )
        self._do_loop_depth -= 1
        if self._do_loop_depth == 0:
            self._in_do_loop = False
        return items[0]  # Return the +LOOP token

    def do_loop(self, items: List[Union[Token, Tree]]) -> List[InstructionMetadata]:
        """
        Transform a DO LOOP control structure.
        
        Grammar rule:
            do_loop: DO block (LOOP | PLUS_LOOP)
            
        This transforms:
        #10 #0 DO     ; limit=10, index=0
           block    ; Loop body
        LOOP

        Into:
        ; Initialize loop parameters
        #10             ; Push limit (10)
        #0              ; Push initial index (0)

        ; Save index and limit to R stack
        >r              ; Save index (0) to R stack
        >r              ; Save limit (10) to R stack

        ; Loop body
        +do_label:      ; Start of loop
        block           ; Execute loop body

        ; Loop control
        r>              ; Get limit
        r>              ; Get index
        1+              ; Increment index
        over over       ; Duplicate both for comparison
        >r              ; Save new index back
        >r              ; Save limit back
        <               ; Compare index < limit
        ZJMP do_label    ; Jump if index < limit
        drop            ; Clean up extra copy of index
        drop            ; Clean up extra copy of limit
        """
        do_token = items[0]  # DO token
        block_tree = items[1]  # block tree
        loop_token = items[2]  # LOOP token
        
        # Generate unique label for loop start
        do_label = self._generate_unique_label("do")
        
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
                # >r : N[T->R,r+1,d-1]
                value=INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->R"] | R_EFFECTS["r+1"] | D_EFFECTS["d-1"],
                token=do_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text=">r  \\ Save index to R stack",
                word_addr=block_instructions[0].word_addr - 2
            ),
            # >r for limit
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                # >r : N[T->R,r+1,d-1]
                value=INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->R"] | R_EFFECTS["r+1"] | D_EFFECTS["d-1"],
                token=do_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text=">r  \\ Save limit to R stack",
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
                # r> : rT[T->N,r-1,d+1]
                # 6000
                # 0B00
                # 0010
                # 000C
                # 0001
                # ----
                # 6B1D
                value=INST_TYPES["alu"] | ALU_OPS["rT"] | STACK_EFFECTS["T->N"] | R_EFFECTS["r-1"] | D_EFFECTS["d+1"], # r>
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="r>  \\ Get limit",
                word_addr=block_instructions[-1].word_addr + 1
            ),
            # r> get index
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["rT"] | STACK_EFFECTS["T->N"] | R_EFFECTS["r-1"] | D_EFFECTS["d+1"], # r>
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="r>  \\ Get index",
                word_addr=block_instructions[-1].word_addr + 2
            ),
            # 1+ increment index
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["T+1"],  # 1+
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="1+  \\ Increment index",
                word_addr=block_instructions[-1].word_addr + 3
            ),
            # over over duplicate both values for next iteration
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->N"] | D_EFFECTS["d+1"], # over
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="over  \\ duplicate for next iteration",
                word_addr=block_instructions[-1].word_addr + 4
            ),
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->N"] | D_EFFECTS["d+1"], # over
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="over  \\ duplicate for next iteration",
                word_addr=block_instructions[-1].word_addr + 5
            ),
            # >r save new index
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->R"] | R_EFFECTS["r+1"] | D_EFFECTS["d-1"], # >r
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text=">r  \\ Save new index back",
                word_addr=block_instructions[-1].word_addr + 6
            ),
            # >r save limit
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->R"] | R_EFFECTS["r+1"] | D_EFFECTS["d-1"], # >r
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text=">r  \\ Save limit back",
                word_addr=block_instructions[-1].word_addr + 7
            ),
            # Compare index < limit
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["N<T"] | D_EFFECTS["d-1"], # <
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="<  \\ Compare index < limit",
                word_addr=block_instructions[-1].word_addr + 8
            ),
            # ZJMP do_label
            InstructionMetadata.from_token(
                inst_type=InstructionType.JUMP,
                value=JUMP_OPS["ZJMP"],
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                label_name=do_label,
                instr_text=f"ZJMP {do_label}  \\ Jump if index < limit",
                word_addr=block_instructions[-1].word_addr + 9
            ),
            # rdrop (first)
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["T"] | R_EFFECTS["r-1"], # rdrop
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="rdrop  \\ Clean up index",
                word_addr=block_instructions[-1].word_addr + 10
            ),
            # rdrop (second)
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["T"] | R_EFFECTS["r-1"], # rdrop
                token=loop_token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text="rdrop  \\ Clean up limit",
                word_addr=block_instructions[-1].word_addr + 11
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

    def is_in_do_loop(self) -> bool:
        """Query if currently inside a DO LOOP."""
        return self._in_do_loop

    def get_do_loop_depth(self) -> int:
        """Get current DO LOOP nesting depth."""
        return self._do_loop_depth

    def _generate_rstack_access(self, offset: int, token: Token) -> List[InstructionMetadata]:
        """Generate instructions to access return stack at given offset.
        For nested DO LOOPs, the stack layout is:
        R: ... k_limit k_index j_limit j_index i_limit i_index (top)
        offset 0 = i (innermost index)
        offset 1 = j (middle index, skip 2 values)
        offset 2 = k (outer index, skip 4 values)
        """
        instructions = []
        pairs_to_skip = offset  # Each level needs to skip one more pair of values
        
        # Get all the values we need to skip through plus our target pair
        saved_values = []
        for i in range(pairs_to_skip + 1):
            # Get limit
            instructions.append(
                InstructionMetadata.from_token(
                    inst_type=InstructionType.BYTE_CODE,
                    value=INST_TYPES["alu"] | ALU_OPS["rT"] |
                          STACK_EFFECTS["T->N"] | R_EFFECTS["r-1"] | D_EFFECTS["d+1"],
                    token=token,
                    filename=self.state.current_file,
                    source_lines=self.state.source_lines,
                    instr_text=f"r>  \\ Get limit pair {i}",
                    word_addr=self.addr_space.get_word_address()
                )
            )
            self.addr_space.advance()
            saved_values.append("limit")

            # Get index
            instructions.append(
                InstructionMetadata.from_token(
                    inst_type=InstructionType.BYTE_CODE,
                    value=INST_TYPES["alu"] | ALU_OPS["rT"] |
                          STACK_EFFECTS["T->N"] | R_EFFECTS["r-1"] | D_EFFECTS["d+1"],
                    token=token,
                    filename=self.state.current_file,
                    source_lines=self.state.source_lines,
                    instr_text=f"r>  \\ Get index pair {i}",
                    word_addr=self.addr_space.get_word_address()
                )
            )
            self.addr_space.advance()
            saved_values.append("index")

        # Now we have our target index on top. Duplicate it for use
        instructions.append(
            InstructionMetadata.from_token(
                inst_type=InstructionType.BYTE_CODE,
                value=INST_TYPES["alu"] | ALU_OPS["T"] |
                      STACK_EFFECTS["T->N"] | D_EFFECTS["d+1"],
                token=token,
                filename=self.state.current_file,
                source_lines=self.state.source_lines,
                instr_text=f"dup  \\ Duplicate {'ijk'[offset]} index for use",
                word_addr=self.addr_space.get_word_address()
            )
        )
        self.addr_space.advance()

        # Special case for the innermost loop (offset == 0)
        if offset == 0 and len(saved_values) == 2:
            # First, restore the duplicate index
            instructions.append(
                InstructionMetadata.from_token(
                    inst_type=InstructionType.BYTE_CODE,
                    value=INST_TYPES["alu"] | ALU_OPS["N"] |
                          STACK_EFFECTS["T->R"] | R_EFFECTS["r+1"] | D_EFFECTS["d-1"],
                    token=token,
                    filename=self.state.current_file,
                    source_lines=self.state.source_lines,
                    instr_text=">r  \\ Save index back",
                    word_addr=self.addr_space.get_word_address()
                )
            )
            self.addr_space.advance()
            
            # Insert a swap to bring the original limit to the top
            instructions.append(
                InstructionMetadata.from_token(
                    inst_type=InstructionType.BYTE_CODE,
                    value=INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->N"],
                    token=token,
                    filename=self.state.current_file,
                    source_lines=self.state.source_lines,
                    instr_text="swap  \\ Bring limit to top, leaving i below",
                    word_addr=self.addr_space.get_word_address()
                )
            )
            self.addr_space.advance()
            
            # Restore the limit
            instructions.append(
                InstructionMetadata.from_token(
                    inst_type=InstructionType.BYTE_CODE,
                    value=INST_TYPES["alu"] | ALU_OPS["N"] |
                          STACK_EFFECTS["T->R"] | R_EFFECTS["r+1"] | D_EFFECTS["d-1"],
                    token=token,
                    filename=self.state.current_file,
                    source_lines=self.state.source_lines,
                    instr_text=">r  \\ Save limit back",
                    word_addr=self.addr_space.get_word_address()
                )
            )
            self.addr_space.advance()
        else:
            # For non-innermost (or more complex) cases, restore all values in reverse order.
            for value_type in reversed(saved_values):
                if value_type == "index":
                    instructions.append(
                        InstructionMetadata.from_token(
                            inst_type=InstructionType.BYTE_CODE,
                            value=INST_TYPES["alu"] | ALU_OPS["N"] |
                                  STACK_EFFECTS["T->R"] | R_EFFECTS["r+1"] | D_EFFECTS["d-1"],
                            token=token,
                            filename=self.state.current_file,
                            source_lines=self.state.source_lines,
                            instr_text=">r  \\ Restore index",
                            word_addr=self.addr_space.get_word_address()
                        )
                    )
                    self.addr_space.advance()
                    
                    if len(saved_values) > 2:
                        instructions.append(
                            InstructionMetadata.from_token(
                                inst_type=InstructionType.BYTE_CODE,
                                value=INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->N"],
                                token=token,
                                filename=self.state.current_file,
                                source_lines=self.state.source_lines,
                                instr_text="swap  \\ Bring next value to top",
                                word_addr=self.addr_space.get_word_address()
                            )
                        )
                        self.addr_space.advance()
                else:  # limit
                    instructions.append(
                        InstructionMetadata.from_token(
                            inst_type=InstructionType.BYTE_CODE,
                            value=INST_TYPES["alu"] | ALU_OPS["N"] |
                                  STACK_EFFECTS["T->R"] | R_EFFECTS["r+1"] | D_EFFECTS["d-1"],
                            token=token,
                            filename=self.state.current_file,
                            source_lines=self.state.source_lines,
                            instr_text=">r  \\ Restore limit",
                            word_addr=self.addr_space.get_word_address()
                        )
                    )
                    self.addr_space.advance()
                    
                    if len(saved_values) > 2:
                        instructions.append(
                            InstructionMetadata.from_token(
                                inst_type=InstructionType.BYTE_CODE,
                                value=INST_TYPES["alu"] | ALU_OPS["N"] | STACK_EFFECTS["T->N"],
                                token=token,
                                filename=self.state.current_file,
                                source_lines=self.state.source_lines,
                                instr_text="swap  \\ Bring next value to top",
                                word_addr=self.addr_space.get_word_address()
                            )
                        )
                        self.addr_space.advance()

        return instructions

