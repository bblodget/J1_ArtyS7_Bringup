// Test file for mixed statement types with whitespace as separator
// This should parse: label instruction instruction macro_def instruction

macro: add       ( a b -- c )        T+N[d-1]       endmacro

: test_label    // Define a label
    2               // Raw number literal 
    3               // Raw number literal 
    add             // macro call
