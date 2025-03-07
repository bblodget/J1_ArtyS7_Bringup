// Test nested includes and complex macros
include "math/math_words.asm"

: start
    #5 #3        // Push 5 and 3
    2dup         // Stack: 5 3 5 3
    plus         // Stack: 5 3 8
    swap         // Stack: 5 8 3
    drop         // Stack: 5 8
    JMP done     // Jump to end

: done
    noop
    JMP done
