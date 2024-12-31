; Arithmetic operations test
; Tests basic arithmetic operations of the J1 processor

start:
    #$1234      ; Load first test value
    #$5678      ; Load second test value
    T+N         ; Add them together (should be 0x68AC)
    DROP        ; Clean up stack

    #$5000      ; Load test value
    #$2000      ; Load value to subtract
    T-N         ; Subtract (should be 0x3000)
    DROP        ; Clean up stack

    #$0005      ; Load test value
    1+          ; Increment (should be 0x0006)
    1-          ; Decrement (back to 0x0005)
    
    #$0004      ; Load test value
    2*          ; Double (should be 0x0008)
    2/          ; Half (back to 0x0004)
    
    JMP start   ; Loop forever
