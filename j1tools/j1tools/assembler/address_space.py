"""
Manages memory layout with ORG directives and collision detection
"""

import logging
from typing import Dict, List, Tuple
from pathlib import Path

class AddressSpace:
    def __init__(self):
        self.current_word_addr = 0x0000
        self.used_ranges: List[Tuple[int, int]] = []
        self.base_address = 0x0000
        self.sections: Dict[str, Dict] = {
            '.code': {'start': 0x0000, 'current': 0x0000},
            '.data': {'start': None, 'current': None}
        }
        self.current_section = '.code'
        self.logger = logging.getLogger("j1asm.addr")

    def set_org(self, address: int) -> None:
        """Set new origin address with collision checking"""
        if address < self.current_word_addr and self.current_section == '.code':
            raise ValueError(f"ORG {address:04x} attempts to move backward in .code section")
            
        if self._check_collision(address):
            raise ValueError(f"Address collision at {address:04x}")
            
        self.current_word_addr = address
        self.sections[self.current_section]['current'] = address
        self.logger.debug(f"ORG set to {address:04x} in {self.current_section}")

    def advance(self, size: int = 1) -> int:
        """Advance address pointer and return previous address"""
        prev_addr = self.current_word_addr
        self.current_word_addr += size
        self.used_ranges.append((prev_addr, prev_addr + size))
        return prev_addr

    def undo_advance(self, size: int = 1) -> None:
        """Undo previous advance operation(s)"""
        if not self.used_ranges:
            raise ValueError("No addresses to retract")
        
        # Remove the last 'size' number of ranges
        for _ in range(size):
            if not self.used_ranges:
                raise ValueError("Cannot retract more addresses than were advanced")
            
            start, end = self.used_ranges.pop()
            self.current_word_addr = start  # Reset to start of removed range
        
        self.logger.debug(f"Retracted to address {self.current_word_addr:04x}")

    def _check_collision(self, address: int) -> bool:
        """Check if address range is already used"""
        for start, end in self.used_ranges:
            if start <= address < end:
                return True
        return False

    def get_word_address(self) -> int:
        """Get current word address"""
        return self.current_word_addr

    def get_byte_address(self) -> int:
        """Get current byte address"""
        return self.current_word_addr * 2