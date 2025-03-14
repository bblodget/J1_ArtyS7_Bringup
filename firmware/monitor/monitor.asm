// J1 Monitor System
// Provides live coding environment with monitor and user program threads

ORG $0000
JMP 'monitor_init        // Boot vector jumps to monitor initialization

ORG $0002
JMP 'irq_handler        // Interrupt vector

include "core/j1_base_macros.asm"      
include "core/j1_extended_macros.asm"   
include "io/terminal_io.asm"

// Monitor system variables (high memory)
// These are at fixed locations in high memory
ORG $7F0              // Reserve last 16 words for system variables
: user_dsp     0 ;    // User data stack pointer save
: user_rsp     0 ;    // User return stack pointer save
: user_pc      0 ;    // User program counter save
: user_st0     0 ;    // User top of stack save

// Monitor initialization
: monitor_init ( -- )
    // Initialize system
    #monitor_prompt user_pc !    // Set initial user PC to prompt
    eint                        // Enable interrupts
    monitor_prompt              // Start monitor prompt
    ;

// Interrupt handler - saves user context and switches to monitor
: irq_handler ( -- )
    // Save user context
    status user_dsp !          // Save data stack pointer
    rstatus user_rsp !         // Save return stack pointer
    T user_st0 !               // Save top of stack
    
    // Switch to monitor context
    monitor_check_input        // Check for monitor commands
    
    // Restore user context and return if no monitor action needed
    user_st0 @ T->N           // Restore top of stack
    user_pc @ JMP             // Return to user code
    ;

// Monitor command check
: monitor_check_input ( -- )
    // Check if UART has data
    $2000 io@ 1 and IF      // Check UART status
        key                    // Get character
        $FF = IF             // Check for command escape
            handle_command     // Process command
        ELSE
            drop              // Discard normal character during interrupt
        THEN
    THEN
    ;

// Monitor prompt
: monitor_prompt ( -- )
    s" J1 Monitor> " type     // Print prompt
    key                       // Wait for command
    handle_command            // Process command
    monitor_prompt            // Loop
    ;

// Command handler
: handle_command ( c -- )
    dup $01 = IF            // Upload command
        drop
        do_upload
    ELSE dup $02 = IF       // Run command
        drop
        do_run
    ELSE dup $03 = IF       // Stop command
        drop
        do_stop
    ELSE                     // Unknown command
        drop
    THEN THEN THEN
    ;

// Upload handler - placeholder
: do_upload ( -- )
    s" Upload mode" type
    $0A emit               // Newline
    ;

// Run handler - placeholder
: do_run ( -- )
    s" Running user program" type
    $0A emit               // Newline
    ;

// Stop handler - placeholder
: do_stop ( -- )
    s" Stopped user program" type
    $0A emit               // Newline
    ;
