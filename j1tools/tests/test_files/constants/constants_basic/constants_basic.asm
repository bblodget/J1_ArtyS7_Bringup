// Basic constant test

ORG $0000

// Define some constants
CONSTANT MAX_VALUE 100
CONSTANT MIN_VALUE 10
CONSTANT ZERO 0
CONSTANT NEGATIVE_ONE -1
CONSTANT HEX_VALUE $ABCD

// Use constants
MAX_VALUE
MIN_VALUE
ZERO
NEGATIVE_ONE
HEX_VALUE

// Define a subroutine
: test_constants
    MAX_VALUE
    MIN_VALUE +
;

// Call the subroutine
test_constants 