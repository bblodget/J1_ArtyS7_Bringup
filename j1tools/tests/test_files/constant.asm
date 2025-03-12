// Test file for constant definitions

// Define some basic constants
.define MAX_VALUE 100
.define MIN_VALUE 10
.define MULTIPLIER 2
.define ASCII_A 'A'
.define SOME_HEX $BEEF

// Define constants that reference other constants
.define TWICE_MAX MAX_VALUE
.define OFFSET 20

// Define a label for the entry point
: main
    #MIN_VALUE      // Push MIN_VALUE onto stack
    #MAX_VALUE      // Push MAX_VALUE onto stack
    #MULTIPLIER     // Push MULTIPLIER onto stack
    T*              // Multiply top of stack
    T+N             // Add together
    
    // Test different constant types
    #ASCII_A        // Push ASCII 'A' (65)
    #SOME_HEX       // Push hex value $BEEF

// Define a reference to main (this should be after the label is defined)
.define ENTRY_POINT main 