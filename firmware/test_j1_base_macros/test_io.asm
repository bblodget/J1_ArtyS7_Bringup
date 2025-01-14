// Test I/O operations
include "core/j1_base_macros.asm"

start:
    // Test UART write (0x1000)
    #48          // Stack: 0x48 ('H' in ASCII)
    #1000        // Stack: 0x48 1000 (UART address)
    io!          // Stack: empty (write 'H' to UART)
    
    // Test UART status read (0x2000)
    #2000        // Stack: 2000 (MISC_IN_ADDR)
    io@          // Stack: status (bit 0: !uart_busy, bit 1: uart_valid)
    
    // Test UART read (0x1000)
    #1000        // Stack: status 1000
    io@          // Stack: status rx_data (if uart_valid was set)
    
    // Test ticks counter (0x4000)
    #4000        // Stack: status rx_data 4000
    io@          // Stack: status rx_data ticks
    
    // Test cycles counter (0x8000)
    #8000        // Stack: status rx_data ticks 8000
    io@          // Stack: status rx_data ticks cycles

done:
    noop
    JMP done