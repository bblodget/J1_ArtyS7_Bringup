#!/usr/bin/env python3

import re
import sys
from pathlib import Path

def update_literals_in_file(file_path):
    """Update literals in a single file from #123/#$ABC format to 123/$ABC format."""
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Track original content for comparison
    original_content = content
    
    # Replace #$XXXX (hex literals) with $XXXX
    content = re.sub(r'#(\$[0-9A-Fa-f]+)', r'\1', content)
    
    # Replace #123 (decimal literals) with 123
    # Be careful not to replace instances where # is used for other purposes
    # This regex looks for # followed by digits, ensuring it's a literal
    content = re.sub(r'#(\d+)(?=[\s,]|$)', r'\1', content)
    
    # Replace #'X' (character literals) with 'X'
    content = re.sub(r'#(\'[^\']+\')', r'\1', content)
    
    # If changes were made, write back to the file
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    
    return False

def update_literals_in_directory(directory_path):
    """Recursively update literals in all .asm files in the given directory."""
    directory = Path(directory_path)
    changed_files = []
    
    # Find all .asm files recursively
    for asm_file in directory.glob('**/*.asm'):
        if update_literals_in_file(asm_file):
            changed_files.append(asm_file)
    
    return changed_files

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "j1tools/tests/test_files"
    
    print(f"Updating literals in .asm files in {directory}...")
    changed_files = update_literals_in_directory(directory)
    
    print(f"Updated {len(changed_files)} files:")
    for file in changed_files:
        print(f"  - {file}") 