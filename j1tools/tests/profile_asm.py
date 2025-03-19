#!/usr/bin/env python

import cProfile
import pstats
import io
from pathlib import Path
from j1tools.assembler.asm import J1Assembler

def profile_assembler():
    # Get the test file path
    test_file = Path(__file__).parent / "test_files" / "control" / "raw_nested_do_loop" / "raw_nested_do_loop.asm"
    
    # Read the source
    with open(test_file, "r") as f:
        source = f.read()
    
    # Create assembler instance
    assembler = J1Assembler(debug=True)
    
    # Run the assembler
    tree = assembler.parse(source, str(test_file))
    assembler.transform(tree)
    
    # Get the bytecodes (this ensures all processing is complete)
    bytecodes = assembler.get_bytecodes()

if __name__ == "__main__":
    # Create a Profile object
    pr = cProfile.Profile()
    
    # Start profiling
    pr.enable()
    
    # Run the assembler
    profile_assembler()
    
    # Stop profiling
    pr.disable()
    
    # Create a Stats object
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    
    # Print the stats
    print("\n=== Top 20 time-consuming functions ===")
    ps.print_stats(20)
    
    # Save detailed stats to a file
    with open('profile_stats.txt', 'w') as f:
        ps.stream = f
        ps.print_stats()
    
    print("\nDetailed stats saved to profile_stats.txt") 