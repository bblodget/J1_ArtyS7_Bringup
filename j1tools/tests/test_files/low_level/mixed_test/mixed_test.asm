// Test file for mixed statement types with whitespace as separator
// This should parse: label instruction instruction macro_def instruction

macro: double  // Define a macro (simplified for test)
   T+N
endmacro

: test_label    // Define a label
    T[d+0]          // ALU operation with modifier
    T[T->N,d-1]     // Another ALU operation
    2               // Raw number literal 
    2               // Raw number literal 
