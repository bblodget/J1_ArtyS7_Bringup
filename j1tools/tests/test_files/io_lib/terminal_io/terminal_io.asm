
include "io/terminal_io.asm"

start:                  // Program entry point
    #$48 CALL emit     // Send 'H' (ASCII 0x48)
    #$69 CALL emit  // Send 'i' (ASCII 0x69)
    #$21 CALL emit  // Send '!' (ASCII 0x21)
    #$0A CALL emit  // Send newline (ASCII 0x0A)

    // Test receive functionality
    // CALL key?       // Check if character available
    // ZJMP no_input   // Skip if no input
    // CALL key        // Read the character
    // CALL emit       // Echo it back

// no_input:
//     // Test 2emit for sending two characters
//     // #$4F #$4B CALL 2emit  // Send "OK" (ASCII 0x4F, 0x4B)
//     // #$0A CALL emit        // Send newline

wait_forever:
     noop
     JMP wait_forever