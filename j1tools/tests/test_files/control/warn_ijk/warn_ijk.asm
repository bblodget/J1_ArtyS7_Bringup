ORG $0000
JMP start

include "core/j1_base_macros.asm"

: start
    // Test using i, j, k outside any loop
    i               // Should warn: used outside DO LOOP
    drop
    j               // Should warn: used outside DO LOOP
    drop
    k               // Should warn: used outside DO LOOP
    drop

    // Single loop - only i valid
    #3 #0 DO
        i           // OK - innermost loop index
        drop
        j           // Should warn: used in non-nested DO LOOP
        drop
        k           // Should warn: insufficient nesting
        drop
    LOOP

    // Double nested - i and j valid
    #3 #0 DO
        #2 #0 DO
            i       // OK - innermost loop index
            drop
            j       // OK - outer loop index
            drop
            k       // Should warn: insufficient nesting
            drop
        LOOP
    LOOP

    // Triple nested - i, j, and k all valid
    #3 #0 DO
        #2 #0 DO
            #4 #0 DO
                k   // OK - outermost loop index
                drop
                j   // OK - middle loop index
                drop
                i   // OK - innermost loop index
                drop
            LOOP
        LOOP
    LOOP
    
: wait_forever
     noop
     JMP wait_forever

