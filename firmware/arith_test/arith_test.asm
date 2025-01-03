; Arithmetic operations test
; Tests basic arithmetic operations of the J1 processor

start:
    ; Test addition 1
    #$1234      ; Load first test value
    #$5678      ; Load second test value
    ADD         ; Add them together (should be 0x68AC)
    DROP        ; Clean up result

    ; Test addition 2
    #$1234      ; Load first test value
    #$5678      ; Load second test value
    +         ; Add them together (should be 0x68AC)
    DROP        ; Clean up result

    ; Test subtraction 1
    #$5000      ; Load first test value
    #$2000      ; Load value to subtract
    SUBTRACT    ; Subtract (should be 0x3000)
    DROP        ; Clean up result

    ; Test subtraction 2
    #$5000      ; Load first test value
    #$2000      ; Load value to subtract
    -           ; Subtract (should be 0x3000)
    DROP        ; Clean up result

    ; Test increment/decrement
    #$0005      ; Load test value
    1+          ; Increment (should be 0x0006)
    1-          ; Decrement (back to 0x0005)
    DROP        ; Clean up result
    
    ; Test double/half
    #$0004      ; Load test value
    2*          ; Double (should be 0x0008)
    2/          ; Half (back to 0x0004)
    DROP        ; Clean up result

    ; Test bitwise operations
    #$FF00      ; Load first test value
    #$0FF0      ; Load second test value
    AND         ; Bitwise AND (should be 0x0F00)
    DROP        ; Clean up result

    #$F0FF      ; Load first test value
    #$0F0F      ; Load second test value
    OR          ; Bitwise OR (should be 0xFFFF)
    DROP        ; Clean up result

    #$F0FF      ; Load first test value
    #$0F0F      ; Load second test value
    XOR          ; Bitwise OR (should be 0xFFF0)
    DROP        ; Clean up result

    #$FFFF      ; Load test value
    INVERT      ; Bitwise NOT (should be 0x0000)
    INVERT      ; Bitwise NOT (should be 0xFFFF)
    DROP        ; Clean up result

    #$0000      ; Load test value
    INVERT      ; Bitwise NOT (should be 0xFFFF)
    INVERT      ; Bitwise NOT (should be 0x0000)
    DROP        ; Clean up result

		; Load -2 onto stack
    #$0002      ; Load test value
    1-		; Subtract 1
    INVERT      ; Bitwise NOT (should be 0xFFFE)
    DROP        ; Clean up result
    
    JMP start   ; Loop forever
