; Test file for comparison operations
; Each test should leave either -1 (true) or 0 (false) on the stack

main:
    ; Test equality (=)
    #5      ; Push 5
    #5      ; Push another 5
    =       ; Should leave -1 (true)
    DROP        ; Clean up result
    
    #5
    #6
    =       ; Should leave 0 (false)
    DROP        ; Clean up result

    ; Test signed less than (<)
    #-5     ; Push -5
    #5      ; Push 5
    <       ; Should leave -1 (true)
    DROP        ; Clean up result
    
    #5
    #-5
    <       ; Should leave 0 (false)
    DROP        ; Clean up result

    ; Test unsigned less than (U<)
    #5
    #10
    U<      ; Should leave -1 (true)
    DROP        ; Clean up result
    
    #10
    #5
    U<      ; Should leave 0 (false)
    DROP        ; Clean up result

    ; Test with +RET optimization
;    : test_eq  ( n1 n2 -- flag )  =+RET ;
;    : test_lt  ( n1 n2 -- flag )  <+RET ;
;    : test_ult ( n1 n2 -- flag ) U<+RET ;