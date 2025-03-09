#!/usr/bin/env python3
"""
Script to rebuild all test files in the test_files directory.
This is useful after making changes to the grammar or other source files.

Usage: python rebuild_tests.py [options]

Options:
  --verbose, -v     Show verbose output from make commands
  --filter, -f STR  Only rebuild tests matching this substring
  --dry-run, -n     Don't run commands, just show what would be done
"""

import os
import subprocess
import argparse
import sys
from pathlib import Path

# ANSI color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def parse_args():
    parser = argparse.ArgumentParser(description='Rebuild all test files')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='Show verbose output from make commands')
    parser.add_argument('--filter', '-f', type=str, default=None,
                        help='Only rebuild tests matching this substring')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help="Don't run commands, just show what would be done")
    return parser.parse_args()

def find_test_directories():
    """Find all directories that might contain testable code."""
    test_files_dir = Path(__file__).parent / 'test_files'
    
    # Validate the test_files directory exists
    if not test_files_dir.exists():
        print(f"{RED}Error: test_files directory not found at {test_files_dir}{RESET}")
        sys.exit(1)
    
    test_dirs = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(test_files_dir):
        root_path = Path(root)
        
        # Check if this directory has a Makefile
        if (root_path / 'Makefile').exists():
            test_dirs.append(root_path)
    
    return test_dirs

def rebuild_test(test_dir, verbose=False, dry_run=False):
    """Run make cleanall and make in the specified directory."""
    try:
        # Store the original directory
        original_dir = os.getcwd()
        
        relative_path = test_dir.relative_to(test_dir.parent.parent)
        print(f"{YELLOW}Rebuilding {BOLD}{relative_path}{RESET}")
        
        # Prepare the commands
        cleanall_cmd = ['make', 'cleanall']
        make_cmd = ['make']
        
        # In dry run mode, just print the commands
        if dry_run:
            print(f"Would run: cd {test_dir} && {' '.join(cleanall_cmd)} && {' '.join(make_cmd)}")
            return True
        
        # Change to the test directory
        os.chdir(test_dir)
        
        # Run make cleanall
        if verbose:
            print(f"Running make cleanall in {test_dir}")
            cleanall_result = subprocess.run(cleanall_cmd, text=True)
        else:
            cleanall_result = subprocess.run(cleanall_cmd, 
                                           capture_output=True,
                                           text=True)
        
        if cleanall_result.returncode != 0:
            print(f"{RED}Error in make cleanall for {relative_path}:{RESET}")
            if not verbose:  # Already shown if verbose
                print(cleanall_result.stderr)
            
            # Return to the original directory
            os.chdir(original_dir)
            return False
        
        # Run make
        if verbose:
            print(f"Running make in {test_dir}")
            make_result = subprocess.run(make_cmd, text=True)
        else:
            make_result = subprocess.run(make_cmd, 
                                       capture_output=True,
                                       text=True)
        
        success = make_result.returncode == 0
        
        if not success:
            print(f"{RED}Error in make for {relative_path}:{RESET}")
            if not verbose:  # Already shown if verbose
                print(make_result.stderr)
        
        # Return to the original directory
        os.chdir(original_dir)
        
        status = f"{GREEN}✓ Success{RESET}" if success else f"{RED}✗ Failed{RESET}"
        print(f"{status} - {relative_path}")
        
        return success
    
    except Exception as e:
        print(f"{RED}Error processing {test_dir}: {e}{RESET}")
        # Make sure we're back in the original directory in case of error
        try:
            os.chdir(original_dir)
        except:
            pass
        return False

def main():
    args = parse_args()
    
    # Find all test directories
    test_dirs = find_test_directories()
    
    # Apply filter if specified
    if args.filter:
        test_dirs = [d for d in test_dirs if args.filter in str(d)]
    
    if not test_dirs:
        print(f"{YELLOW}No test directories found{RESET}")
        if args.filter:
            print(f"Check your filter: '{args.filter}'")
        return
    
    print(f"Found {len(test_dirs)} test directories to rebuild")
    
    # Store the current directory to restore it later
    original_dir = os.getcwd()
    
    try:
        # Process test directories sequentially
        results = []
        
        for test_dir in test_dirs:
            success = rebuild_test(test_dir, args.verbose, args.dry_run)
            results.append((test_dir, success))
        
        # Only show summary if we actually ran the commands
        if not args.dry_run:
            # Print summary
            success_count = sum(1 for _, success in results if success)
            print(f"\n{BOLD}Summary:{RESET}")
            print(f"Rebuilt {success_count} of {len(test_dirs)} tests successfully")
            
            if success_count < len(test_dirs):
                failed_dirs = [str(d.relative_to(d.parent.parent)) for d, success in results if not success]
                print(f"{RED}Failed tests:{RESET}")
                for failed in failed_dirs:
                    print(f"  - {failed}")
    
    finally:
        # Return to the original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    main() 