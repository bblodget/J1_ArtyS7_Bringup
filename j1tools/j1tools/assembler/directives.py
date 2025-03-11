# directives.py

import logging
from typing import List
from .asm_types import AssemblerState

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