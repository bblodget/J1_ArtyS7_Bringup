; UART Echo Program
; Continuously echo characters from UART RX to TX

start:
        LIT #4002     ; Push UART_VALID_ADDR
        IO@           ; Read UART valid status
        DUP           ; Duplicate valid status
        0BRANCH start ; If not valid, branch to start
        DROP          ; Drop valid flag
        LIT #4000     ; Push UART_RX_ADDR
        IO@           ; Read from UART
        DUP           ; Duplicate received byte
        CALL check_busy ; Check if UART is busy
        LIT #4001     ; Push UART_TX_ADDR
        IO!           ; Write to UART
        JMP start     ; Jump back to start

check_busy:
        LIT #4003     ; Push UART_BUSY_ADDR
        IO@           ; Check if UART is busy
        DUP           ; Duplicate busy status
        0BRANCH done  ; If not busy, return
        DROP          ; Drop busy flag
        JMP check_busy ; Keep checking if busy

done:
        DROP          ; Drop busy flag
        RET           ; Return to caller (0x6080)