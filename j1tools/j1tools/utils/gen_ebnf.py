#!/usr/bin/env python3
"""
Generate RR-compatible EBNF from Lark grammar files.

This script converts a Lark grammar file to EBNF syntax that is compatible with 
the RR - Railroad Diagram Generator (https://github.com/GuntherRademacher/rr).
"""

import re
import argparse
import sys

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert Lark grammar to RR-compatible EBNF.'
    )
    parser.add_argument(
        'input_file', 
        help='Path to the Lark grammar file'
    )
    parser.add_argument(
        '-o', '--output', 
        help='Output file (default: stdout)',
        default=None
    )
    parser.add_argument(
        '--format', 
        choices=['rr', 'w3c'], 
        default='rr',
        help='Output format: rr (Railroad) or w3c (W3C EBNF) (default: rr)'
    )
    
    return parser.parse_args()

def extract_rules_from_lark(grammar_text):
    """Extract rule definitions from Lark grammar text."""
    rule_pattern = re.compile(r'^([?]?)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*?)$', re.MULTILINE)
    rule_definitions = []

    for match in rule_pattern.finditer(grammar_text):
        optional = match.group(1) == '?'
        rule_name = match.group(2)
        line_production = match.group(3).strip()
        
        # Skip token definitions (uppercase with regex patterns)
        if rule_name.isupper() and not line_production.startswith('rule'):
            continue
            
        # Skip import and directive lines
        if line_production.startswith('%'):
            continue
            
        # Find the complete production for this rule
        start_pos = match.start()
        next_match = rule_pattern.search(grammar_text, match.end())
        end_pos = next_match.start() if next_match else len(grammar_text)
        
        # Extract the full rule text
        rule_text = grammar_text[start_pos:end_pos].strip()
        
        # Parse out just the production part (after the colon)
        production_text = rule_text.split(':', 1)[1].strip()
        
        # Remove any line comments
        production_lines = []
        for line in production_text.split('\n'):
            if '//' in line:
                line = line.split('//', 1)[0].strip()
            if line.strip():
                production_lines.append(line.strip())
        
        production = ' '.join(production_lines)
        rule_definitions.append((optional, rule_name, production))

    # Filter out token definitions
    non_token_rules = []
    for optional, name, production in rule_definitions:
        # Skip directive rules and token definitions
        if name.startswith('%') or production.startswith('%'):
            continue
        # Skip token definitions with regex patterns
        if name.isupper() and (production.startswith('/') or production.startswith('"')):
            continue
        non_token_rules.append((optional, name, production))
    
    return non_token_rules

def lark_to_w3c_ebnf(production):
    """Convert Lark production to W3C EBNF syntax."""
    # Clean up and normalize whitespace
    production = re.sub(r'\s+', ' ', production.strip())
    
    # Replace Lark's operators with EBNF notation
    production = re.sub(r'(\S+)\s*\*', r'\1 {0,}', production)  # token* -> token {0,}
    production = re.sub(r'(\S+)\s*\+', r'\1 {1,}', production)  # token+ -> token {1,}
    production = re.sub(r'(\S+)\s*\?', r'\1 [1]', production)  # token? -> token [1]
    
    # Replace OR alternatives with |
    production = re.sub(r'\s*\|\s*', ' | ', production)
    
    # Quote terminal symbols (tokens in all uppercase)
    def quote_terminal(match):
        term = match.group(1)
        if term.isupper() and not term.startswith('_'):
            return f'"{term}"'
        return term
    
    production = re.sub(r'\b([A-Z][A-Z0-9_]*)\b', quote_terminal, production)
    
    return production.strip()

def lark_to_rr_ebnf(production):
    """Convert Lark production to RR-compatible EBNF syntax."""
    # Clean up and normalize whitespace
    production = re.sub(r'\s+', ' ', production.strip())
    
    # Replace OR alternatives with |
    production = re.sub(r'\s*\|\s*', ' | ', production)
    
    # Quote terminal symbols (tokens in all uppercase)
    def quote_terminal(match):
        term = match.group(1)
        if term.isupper() and not term.startswith('_'):
            return f'"{term}"'
        return term
    
    production = re.sub(r'\b([A-Z][A-Z0-9_]*)\b', quote_terminal, production)
    
    return production.strip()

def generate_w3c_ebnf(rules):
    """Generate W3C-style EBNF from parsed rules."""
    output = []
    output.append("(*")
    output.append("  J1 Forth Assembler Grammar - W3C EBNF Format")
    output.append("*)")
    output.append("")
    
    for optional, rule_name, production in rules:
        # Format the rule name
        formatted_name = rule_name
        # If it's an optional rule, use square brackets in EBNF
        if optional:
            formatted_name = f"[{rule_name}]"
        
        # Format the production in EBNF
        ebnf_production = lark_to_w3c_ebnf(production)
        
        # Output the rule
        output.append(f"{formatted_name} ::= {ebnf_production}")
        output.append("")
    
    return "\n".join(output)

def generate_rr_ebnf(rules):
    """Generate RR-compatible EBNF from parsed rules."""
    output = []
    output.append("/* J1 Forth Assembler Grammar - RR Compatible Format */")
    output.append("")
    
    for optional, rule_name, production in rules:
        # Format the rule name
        formatted_name = rule_name
        
        # Format the production in EBNF
        ebnf_production = lark_to_rr_ebnf(production)
        
        # Output the rule with RR-specific formatting
        if len(rule_name) > 7:
            output.append(f"{rule_name} ")
            output.append(f"         ::= {ebnf_production}")
        else:
            output.append(f"{rule_name.ljust(8)}::= {ebnf_production}")
    
    return "\n".join(output)

def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    try:
        with open(args.input_file, 'r') as f:
            grammar_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        return 1
    
    # Extract rules from the grammar
    rules = extract_rules_from_lark(grammar_text)
    
    # Sort rules to ensure 'start' rule is first
    sorted_rules = []
    # Add start rule first
    for rule in rules:
        if rule[1] == 'start':
            sorted_rules.append(rule)
            break
    
    # Add remaining rules
    for rule in rules:
        if rule[1] != 'start':
            sorted_rules.append(rule)
    
    # Generate EBNF based on selected format
    if args.format == 'w3c':
        output = generate_w3c_ebnf(sorted_rules)
    else:  # rr format
        output = generate_rr_ebnf(sorted_rules)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
