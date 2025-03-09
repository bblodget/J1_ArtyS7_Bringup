#!/usr/bin/env python3
"""
Script to recursively find Makefiles and run 'make cleanall' followed by 'make'.
This is useful after making changes to the grammar or source files in any directory.

Usage: rebuild_make [options]

Options:
  --verbose, -v       Show verbose output from make commands
  --filter, -f STR    Only rebuild directories matching this substring
  --dry-run, -n       Don't run commands, just show what would be done
  --directory, -d DIR Start searching from this directory (default: current directory)
  --help, -h          Show this help message and exit
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
    parser = argparse.ArgumentParser(
        description='Recursively find Makefiles and run make cleanall followed by make'
    )
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='Show verbose output from make commands')
    parser.add_argument('--filter', '-f', type=str, default=None,
                        help='Only rebuild directories matching this substring')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help="Don't run commands, just show what would be done")
    parser.add_argument('--directory', '-d', type=str, default=os.getcwd(),
                        help='Start searching from this directory (default: current directory)')
    return parser.parse_args()

def find_make_directories(start_dir):
    """Find all directories that contain a Makefile."""
    start_path = Path(start_dir)
    
    # Validate the start directory exists
    if not start_path.exists():
        print(f"{RED}Error: Start directory not found at {start_path}{RESET}")
        sys.exit(1)
    
    make_dirs = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(start_path):
        root_path = Path(root)
        
        # Check if this directory has a Makefile
        if (root_path / 'Makefile').exists():
            make_dirs.append(root_path)
    
    return make_dirs

def rebuild_directory(dir_path, verbose=False, dry_run=False):
    """Run make cleanall and make in the specified directory."""
    try:
        # Store the original directory
        original_dir = os.getcwd()
        
        # Get a relative path for display, relative to starting directory if possible
        try:
            relative_path = dir_path.relative_to(original_dir)
            if str(relative_path) == '.':
                display_path = dir_path.name
            else:
                display_path = relative_path
        except ValueError:
            # If we can't get a relative path, use the full path
            display_path = dir_path
        
        print(f"{YELLOW}Rebuilding {BOLD}{display_path}{RESET}")
        
        # Prepare the commands
        cleanall_cmd = ['make', 'cleanall']
        make_cmd = ['make']
        
        # In dry run mode, just print the commands
        if dry_run:
            print(f"Would run: cd {dir_path} && {' '.join(cleanall_cmd)} && {' '.join(make_cmd)}")
            return True
        
        # Change to the target directory
        os.chdir(dir_path)
        
        # Run make cleanall
        if verbose:
            print(f"Running make cleanall in {dir_path}")
            cleanall_result = subprocess.run(cleanall_cmd, text=True)
        else:
            cleanall_result = subprocess.run(cleanall_cmd, 
                                           capture_output=True,
                                           text=True)
        
        if cleanall_result.returncode != 0:
            print(f"{RED}Error in make cleanall for {display_path}:{RESET}")
            if not verbose:  # Already shown if verbose
                print(cleanall_result.stderr)
            
            # Return to the original directory
            os.chdir(original_dir)
            return False
        
        # Run make
        if verbose:
            print(f"Running make in {dir_path}")
            make_result = subprocess.run(make_cmd, text=True)
        else:
            make_result = subprocess.run(make_cmd, 
                                       capture_output=True,
                                       text=True)
        
        success = make_result.returncode == 0
        
        if not success:
            print(f"{RED}Error in make for {display_path}:{RESET}")
            if not verbose:  # Already shown if verbose
                print(make_result.stderr)
        
        # Return to the original directory
        os.chdir(original_dir)
        
        status = f"{GREEN}✓ Success{RESET}" if success else f"{RED}✗ Failed{RESET}"
        print(f"{status} - {display_path}")
        
        return success
    
    except Exception as e:
        print(f"{RED}Error processing {dir_path}: {e}{RESET}")
        # Make sure we're back in the original directory in case of error
        try:
            os.chdir(original_dir)
        except:
            pass
        return False

def main():
    args = parse_args()
    
    # Get absolute path of the starting directory
    start_dir = os.path.abspath(args.directory)
    
    # Find all directories with Makefiles
    make_dirs = find_make_directories(start_dir)
    
    # Apply filter if specified
    if args.filter:
        make_dirs = [d for d in make_dirs if args.filter in str(d)]
    
    if not make_dirs:
        print(f"{YELLOW}No Makefiles found{RESET}")
        if args.filter:
            print(f"Check your filter: '{args.filter}'")
        return
    
    print(f"Found {len(make_dirs)} directories with Makefiles to rebuild")
    
    # Store the current directory to restore it later
    original_dir = os.getcwd()
    
    try:
        # Process directories sequentially
        results = []
        
        for dir_path in make_dirs:
            success = rebuild_directory(dir_path, args.verbose, args.dry_run)
            results.append((dir_path, success))
        
        # Only show summary if we actually ran the commands
        if not args.dry_run:
            # Print summary
            success_count = sum(1 for _, success in results if success)
            print(f"\n{BOLD}Summary:{RESET}")
            print(f"Rebuilt {success_count} of {len(make_dirs)} directories successfully")
            
            if success_count < len(make_dirs):
                # Try to get relative paths for failed directories
                failed_dirs = []
                for d, success in results:
                    if not success:
                        try:
                            rel_path = d.relative_to(original_dir)
                            failed_dirs.append(str(rel_path))
                        except ValueError:
                            failed_dirs.append(str(d))
                
                print(f"{RED}Failed directories:{RESET}")
                for failed in failed_dirs:
                    print(f"  - {failed}")
    
    finally:
        # Return to the original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    main() 