; Test file for comparison operations
; Each test should leave either -1 (true) or 0 (false) on the stack

main:
    CALL test_eq_true DROP
    CALL test_eq_false DROP
    CALL test_lt_true DROP
    CALL test_lt_false DROP
    CALL test_ult_true DROP
    CALL test_ult_false DROP

    JMP main

test_eq_true:
    #5      ; Push 5
    #5      ; Push another 5
    =+RET       ; Should leave -1 (true)
    
test_eq_false:
    #5
    #6
    =+RET       ; Should leave 0 (false)

test_lt_true:
    ; Test signed less than (<)
    ; Construct -5 manually: abs(5) 1- INVERT
    #5      ; Push absolute value
    1-      ; Decrement
    INVERT  ; Invert bits to get -5
    #5      ; Push 5
    <+RET       ; Should leave -1 (true)
    
test_lt_false:
    #5      ; Push 5
    #5      ; Push absolute value for -5
    1-      ; Decrement
    INVERT  ; Invert bits to get -5
    <+RET   ; Should leave 0 (false)

test_ult_true:
    ; Test unsigned less than (U<)
    #5
    #10
    U<+RET   ; Should leave -1 (true)
    
test_ult_false:
    #10
    #5
    U<+RET   ; Should leave 0 (false)