; Arithmetic operations with RET test
; Tests arithmetic operations combined with RET of the J1 processor

; Main test loop
start:
    CALL add_test       ; Test addition with RET
    DROP               ; Clean up result
    
    CALL add_alt_test  ; Test alternative addition syntax
    DROP               ; Clean up result
    
    CALL sub_test      ; Test subtraction with RET
    DROP               ; Clean up result
    
    CALL sub_alt_test  ; Test alternative subtraction syntax
    DROP               ; Clean up result
    
    CALL inc_test      ; Test increment with RET
    DROP               ; Clean up result
    
    CALL dec_test      ; Test decrement with RET
    DROP               ; Clean up result
    
    CALL double_test   ; Test double with RET
    DROP               ; Clean up result
    
    CALL half_test     ; Test half with RET
    DROP               ; Clean up result
    
    CALL and_test      ; Test AND with RET
    DROP               ; Clean up result
    
    CALL or_test       ; Test OR with RET
    DROP               ; Clean up result
    
    CALL xor_test      ; Test XOR with RET
    DROP               ; Clean up result
    
    CALL invert_test   ; Test INVERT with RET
    DROP               ; Clean up result

    JMP start         ; Loop forever

; Test addition with return
add_test:
    #$1234      ; Load first test value
    #$5678      ; Load second test value
    ++RET       ; Add and return (should be 0x68AC)

add_alt_test:
    #$1234      ; Load first test value
    #$5678      ; Load second test value
    ADD+RET     ; Alternative syntax, same result

; Test subtraction with return
sub_test:
    #$5000      ; Load first test value
    #$2000      ; Load value to subtract
    -+RET       ; Subtract and return (should be 0x3000)

sub_alt_test:
    #$5000      ; Load first test value
    #$2000      ; Load value to subtract
    SUBTRACT+RET ; Alternative syntax, same result

; Test increment/decrement with return
inc_test:
    #$0005      ; Load test value
    1++RET      ; Increment and return (should be 0x0006)

dec_test:
    #$0005      ; Load test value
    1-+RET      ; Decrement and return (should be 0x0004)

; Test double/half with return
double_test:
    #$0004      ; Load test value
    2*+RET      ; Double and return (should be 0x0008)

half_test:
    #$0008      ; Load test value
    2/+RET      ; Half and return (should be 0x0004)

; Test bitwise operations with return
and_test:
    #$FF00      ; Load first test value
    #$0FF0      ; Load second test value
    AND+RET     ; Bitwise AND and return (should be 0x0F00)

or_test:
    #$F0FF      ; Load first test value
    #$0F0F      ; Load second test value
    OR+RET      ; Bitwise OR and return (should be 0xFFFF)

xor_test:
    #$F0FF      ; Load first test value
    #$0F0F      ; Load second test value
    XOR+RET     ; Bitwise XOR and return (should be 0xFF00)

invert_test:
    #$FFFF      ; Load test value
    INVERT+RET  ; Bitwise NOT and return (should be 0x0000)
