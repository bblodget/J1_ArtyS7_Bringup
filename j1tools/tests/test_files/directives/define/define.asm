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
    #10              // Push MIN_VALUE (10) onto stack
    #100             // Push MAX_VALUE (100) onto stack 
    T+N[d-1]         // Add top two stack items

: wait_forever
    T[d+0]           // NOOP
    JMP 'wait_forever // Loop forever

