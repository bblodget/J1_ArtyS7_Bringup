; Simple test program
; Pushes two numbers and adds them
; Uses subroutine calls and return
; Uses the stack and return stack
start:                   ; Note the colon after label
    #$2A                 ; Push hex 2A (decimal 42)
    #10                  ; Push decimal 10
    CALL add_nums        ; Call our addition subroutine
    N[d-1]               ; DROP the result
    JMP wait_forever     ; Jump to end of program

add_nums:                ; Note the colon after label
     T+N[d-1]            ; Add top two stack items
     T[T->R,r+1]         ; Save result to return stack (push, don't overwrite)
     T[r-1]              ; Pop our saved value to T
     T[RET,r-1]          ; Return to caller

wait_forever:
    T[d+0]               ; NOOP
    JMP wait_forever     ; Loop forever