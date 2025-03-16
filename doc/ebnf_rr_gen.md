# J1 Grammar Visualization

This document describes how to generate and visualize the J1 Forth Assembler grammar using EBNF (Extended Backus-Naur Form) and railroad diagrams.

## What is EBNF?

EBNF (Extended Backus-Naur Form) is a formal notation used to describe the syntax of computer languages. It provides a concise and precise way to specify the grammar rules of a language.

## What are Railroad Diagrams?

Railroad diagrams are a graphical representation of a grammar, showing the flow of syntax elements in a visual way that's easier to understand than raw EBNF notation. They're called "railroad diagrams" because they resemble train tracks with various branches and paths.

## Generating EBNF from Lark Grammar

The J1 tools package includes a utility called `gen_ebnf` that can convert our Lark grammar to EBNF formats:

### Using the gen_ebnf Utility

After installing the j1tools package, you can use the gen_ebnf command directly:

```bash
# Navigate to your project root
cd ~/Dev/J1_ArtyS7_Bringup

# Generate RR-compatible EBNF
gen_ebnf j1tools/j1tools/assembler/j1.lark -o j1_rr_grammar.ebnf

# Or generate W3C-style EBNF
gen_ebnf j1tools/j1tools/assembler/j1.lark --format w3c -o j1_w3c_grammar.ebnf
```

Alternatively, you can run the script directly:

```bash
# Using the Python script directly
python j1tools/j1tools/utils/gen_ebnf.py j1tools/j1tools/assembler/j1.lark -o j1_rr_grammar.ebnf
```

## Creating Railroad Diagrams with RR

The [RR - Railroad Diagram Generator](https://github.com/GuntherRademacher/rr) is a powerful tool for converting EBNF to visual railroad diagrams.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GuntherRademacher/rr.git
   cd rr
   ```

2. Build the project:
   ```bash
   ./gradlew
   ```

### Generating Diagrams

1. Using the web interface:
   ```bash
   # Start the web application
   java -jar build/libs/rr.war -gui
   ```
   
   Then open your browser to http://localhost:8080/ and paste your EBNF into the text area.

2. Using the command line:
   ```bash
   # Generate HTML with embedded diagrams
   java -jar build/libs/rr.war -out:j1_diagrams.html path/to/j1_rr_grammar.ebnf
   
   # Generate PNG diagrams
   java -jar build/libs/rr.war -png -out:j1_diagrams.html path/to/j1_rr_grammar.ebnf
   ```

### Viewing Diagrams

Open the generated HTML file in your web browser:
```bash
xdg-open j1_diagrams.html  # Linux
open j1_diagrams.html      # macOS
```

## Example

Here's a complete example workflow:

```bash
# Generate RR-compatible EBNF
gen_ebnf j1tools/j1tools/assembler/j1.lark > j1_rr_grammar.ebnf

# Generate railroad diagrams
cd ~/Dev/rr
java -jar build/libs/rr.war -out:~/Dev/J1_ArtyS7_Bringup/doc/j1_railroad_diagrams.html ~/Dev/J1_ArtyS7_Bringup/j1_rr_grammar.ebnf

# View the diagrams
xdg-open ~/Dev/J1_ArtyS7_Bringup/doc/j1_railroad_diagrams.html
```

## Important Notes

1. Grammar Updates: If you update the Lark grammar file (j1.lark), you'll need to regenerate the EBNF and railroad diagrams.

2. RR Compatibility: The RR tool expects EBNF in a specific format, which is why we use the `-format rr` option when generating EBNF.

3. Diagram Customization: RR supports various options for customizing the diagrams, including color schemes, spacing, and output formats. See the RR documentation for more details.

## Resources

- [RR - Railroad Diagram Generator](https://github.com/GuntherRademacher/rr)
- [Online RR Interface](https://www.bottlecaps.de/rr/ui)
- [W3C EBNF Notation](https://www.w3.org/TR/xml/#sec-notation)
