; Stack Operation Test Program
; Initial stack: empty

; Test DUP
#42             ; ( 42 )
DUP             ; ( 42 42 )

; Test OVER
#24             ; ( 42 42 24 )
OVER            ; ( 42 42 24 42 )

; Test SWAP
SWAP            ; ( 42 42 42 24 )

; Test NIP
NIP             ; ( 42 42 24 )

; Test DROP
DROP            ; ( 42 42 )

; Test NOOP (should not affect stack)
NOOP            ; ( 42 42 )

; Test Return Stack Operations
DUP             ; ( 42 42 42 )
>R              ; ( 42 42 )     R: ( 42 )
DUP             ; ( 42 42 42 )  R: ( 42 )
>R              ; ( 42 42 )     R: ( 42 42 )
R@              ; ( 42 42 42 )  R: ( 42 42 )
R>              ; ( 42 42 42 42 ) R: ( 42 )
R>              ; ( 42 42 42 42 42 ) R: ( )

; Final stack should be ( 42 42 42 42 42 )