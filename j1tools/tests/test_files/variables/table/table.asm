// Table Access Test with Tick Operator

include "core/j1_base_macros.asm"      // Base J1 operations
include "core/j1_dualport_macros.asm" // Dualport operations

// Jump to start
JMP 'start

// @ definition for quickstore (not dualport)
//: @ ( addr -- x )
//     #$4000 or >r ;

: my_table
    $10, $20, $30, $40, $50,  // Table with five values

: start
    // Read first value from table
    'my_table @            // Get value at my_table[0] = 10

    // Read the second valued from the table
    'my_table #2 + @       // Get value at my_table[1] = 20

    // Read the third value from the table
    'my_table #4 + @       // Get value at my_table[2] = 30

    // Read the fourth value from the table
    'my_table #6 + @       // Get value at my_table[3] = 40

    // Read the fifth value from the table
    'my_table #8 + @       // Get value at my_table[4] = 50

    // Modify the second value in the table
    #$99 'my_table #2 + !   // Store $99 at my_table[1]

    // Read the modified value from the table
    'my_table #2 + @       // Get value at my_table[1] = $99
    
    // Jump to end
    JMP 'end
    
: end
    noop
    JMP 'end

