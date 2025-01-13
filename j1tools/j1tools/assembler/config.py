"""
Configuration management for J1 assembler.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional

class AssemblerConfig:
    """Manages configuration settings for the J1 assembler."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = logging.getLogger("j1asm.config")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        
        # Initialize paths
        self.include_paths: List[Path] = []
        self.stdlib_enabled = True
        
        # Get the default library path relative to this file
        self.stdlib_path = Path(__file__).parent / 'lib'
        
        # Create stdlib directory if it doesn't exist
        if not self.stdlib_path.exists():
            raise FileNotFoundError(f"Standard library directory not found: {self.stdlib_path}")
            
    def add_include_path(self, path: str) -> None:
        """Add a new include search path."""
        resolved_path = Path(path).resolve()
        if resolved_path not in self.include_paths:
            self.include_paths.append(resolved_path)
            self.logger.debug(f"Added include path: {resolved_path}")
            
    def resolve_include(self, filename: str, current_dir: str) -> Optional[Path]:
        """
        Resolve include file path searching in this order:
        1. Current directory
        2. Explicit include paths
        3. Standard library (if enabled)
        
        Returns:
            Path object if file is found, None otherwise
        """
        self.logger.debug(f"Resolving include: {filename} from {current_dir}")
        
        # First check current directory
        current_path = Path(current_dir) / filename
        if current_path.exists():
            self.logger.debug(f"Found in current directory: {current_path}")
            return current_path
            
        # Check explicit include paths
        for path in self.include_paths:
            full_path = path / filename
            if full_path.exists():
                self.logger.debug(f"Found in include path: {full_path}")
                return full_path
                
        # Check standard library
        if self.stdlib_enabled:
            stdlib_path = self.stdlib_path / filename
            if stdlib_path.exists():
                self.logger.debug(f"Found in stdlib: {stdlib_path}")
                return stdlib_path
                
        self.logger.debug(f"File not found: {filename}")
        return None
    
    def disable_stdlib(self) -> None:
        """Disable the standard library include path."""
        self.stdlib_enabled = False
        self.logger.debug("Standard library disabled")
    
    def enable_stdlib(self) -> None:
        """Enable the standard library include path."""
        self.stdlib_enabled = True
        self.logger.debug("Standard library enabled")
    
    @property
    def search_paths(self) -> List[Path]:
        """Return all active search paths in order."""
        paths = self.include_paths.copy()
        if self.stdlib_enabled:
            paths.append(self.stdlib_path)
        return paths