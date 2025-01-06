; UART Echo Program
; Print "hi" then continuously echo characters from UART RX to TX

;UART_ADDR      = 0x1000  // UART RX/TX data
;MISC_IN_ADDR   = 0x2000  // Status register where:
;                         //   bit 0 = !uart_busy (ready to transmit)
;                         //   bit 1 = uart_valid (data available)

start:
        ; Print 'h'
        ;CALL check_busy   ; Wait until UART is ready
        LIT #68          ; ASCII 'h' (0x68)
        LIT #1000        ; UART_ADDR
        IO!              ; Write to UART

        ; Print 'i'
        ;CALL check_busy   ; Wait until UART is ready
        LIT #69          ; ASCII 'i' (0x69)
        LIT #1000        ; UART_ADDR
        IO!              ; Write to UART

echo_loop:
        LIT #2000        ; Push MISC_IN_ADDR
        IO@              ; Read UART status
        LIT #2           ; Mask for UART_VALID bit (bit 1)
        AND              ; Check if data is available
        0BRANCH echo_loop ; If no data, branch to echo_loop
        LIT #1000        ; Push UART_ADDR
        IO@              ; Read from UART
        DUP              ; Duplicate received byte
        CALL check_busy  ; Check if UART is busy
        LIT #1000        ; Push UART_ADDR
        IO!              ; Write to UART
        JMP echo_loop    ; Jump back to echo_loop

check_busy:
        LIT #2000        ; Push MISC_IN_ADDR
        IO@              ; Read status register
        LIT #1           ; Mask for !UART_BUSY bit (bit 0)
        AND              ; Check if ready to transmit
        0BRANCH check_busy ; If busy (bit=0), keep checking
        RET              ; Return to caller